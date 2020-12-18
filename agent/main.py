import time
import frida
import sys
import argparse


def go_frida(code, mode):
    print(mode)
    device = frida.get_usb_device()
    
    if mode.get("mode") == "force":
        pid = device.get_frontmost_application().pid
    elif mode.get("mode") == "spawn":
        pid = device.spawn(mode.get("id"))
    elif mode.get("mode") == "attach":
        pid = device.get_process(mode.get("id")).pid

    session = device.attach(pid)
    script = session.create_script(code)

    def on_message(message, payload):
        print(str(message) +  " " + str(payload))
        
    script.on("message", on_message)
    script.load()

    if mode.get("mode") == "spawn":
        print("spawn")
        device.resume(pid)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s","--spawn",help="spawn Android Identifier or iOS Identifier in 'frida-ps -Ua'")
    parser.add_argument("-a","--attach",help="attach Android Identifier or iOS Name in 'frida-ps -Ua'")
    parser.add_argument("-F","--attach-frontmost", help="attach 到当前前台 App", default=False, action='store_true')
    parser.add_argument("-i", "--include-method", help="模糊匹配要 hook 的 Java 或 ObjC 方法", action='append', metavar="JAVA_OR_OBJC_METHOD", default=[])
    parser.add_argument("-b", "--backtrace", help="输出方法执行的堆栈信息，默认是 false",default=False, action='store_true')
    parser.add_argument("-d", "--duration", help="输出方法执行的开始时间点与结束时间点，默认是 false", default=False, action='store_true')
    
    return parser.parse_args()

def main():
    args = parse_args()
    include_method = args.include_method.__str__()
    backtrace = "true" if args.backtrace else "false"
    duration = "true" if args.duration else "false"
    spawn = "true" if args.spawn != None else "false"

    code = script_code % (include_method, backtrace, duration, spawn)

    mode = None
    if args.attach_frontmost:
        mode = {"mode":"force"}
    elif args.spawn != None:
        mode = {"mode":"spawn","id":args.spawn}
    elif args.attach != None:
        mode = {"mode":"attach","id":args.attach}

    if mode == None:
        print("请至少指定 -s、-a、-F 其中一种模式")
        return
    else:
        go_frida(code, mode)
        while True:
            time.sleep(10 * 1000)

script_code = r"""
let _include_method = %s
let _backtrace = %s
let _duration = %s
let _spawn = %s

class AndroidMode {
    static include_java_method = []
    static backtrace = false
    static duration = false
    static spawn = false
    static depth = 0

    static init(include_method, backtrace, duration, spawn) {
        this.include_java_method = include_method;
        this.backtrace = backtrace;
        this.duration = duration;
        this.spawn = spawn;

        console.log("\nAndroidMode init:");
        console.log("\tinclude_method: " + this.include_java_method);
        console.log("\tbacktrace: " + this.backtrace);
        console.log("\tduration: " + this.duration);
        console.log("\tspawn: " + this.spawn);

        Java.perform(function () {
            if (spawn) {
                AndroidMode.beforeAppCreate(function () {
                    AndroidMode.alwaysEnableLog();
                    AndroidMode.traceJavaMethod();
                })
            } else {
                AndroidMode.alwaysEnableLog();
                AndroidMode.traceJavaMethod();
            }
        })
    }

    static beforeAppCreate(callback) {
        Java.use("android.app.Application").onCreate.implementation = function () {
            callback();
            this.onCreate();
        }
    }

    static alwaysEnableLog() {
        var SensorsDataAPI = Java.use("com.sensorsdata.analytics.android.sdk.SensorsDataAPI");
        SensorsDataAPI.enableLog.implementation = function (enable) {
            this.enableLog(true);
        }

        var SAConfigOptions = Java.use("com.sensorsdata.analytics.android.sdk.SAConfigOptions");
        SAConfigOptions.enableLog.implementation = function (enable) {
            return this.enableLog(true);
        }

        var SALog = Java.use("com.sensorsdata.analytics.android.sdk.SALog");
        SALog.setEnableLog.implementation = function (isEnableLog) {
            this.setEnableLog(true);
        }

        if (!this.spawn) {
            SensorsDataAPI.sharedInstance().enableLog(true);
        }
        console.log("\nSDK 日志开启成功。")
    }

    static traceJavaMethod() {
        let groups;
        for (let query of this.include_java_method) {
            groups = Java.enumerateMethods(query).concat(groups);
        }
        groups.pop(null)

        this.log("\n以下方法已被成功替换：");
        for (let matchGroup of groups) {
            for (let matchClass of matchGroup['classes']) {
                let className = matchClass['name'];
                for (let matchMethod of matchClass['methods']) {
                    if (matchMethod.endsWith("[XposedHooked]")) {
                        continue;
                    }
                    // 遍历替换所有的 overload 方法实现
                    let overloads = Java.use(className)[matchMethod].overloads;
                    for (let overload of overloads) {
                        overload.implementation = function () {
                            try {
                                let methodSignature = AndroidMode.buildSignature(className, matchMethod, arguments)
                                AndroidMode.printInfoBeforeMethodExecute(methodSignature, arguments)
                                // 调用原方法
                                let result = this[matchMethod].apply(this, arguments);
                                AndroidMode.printInfoAfterMethodExecute(methodSignature, result)
                                return result;
                            } catch (error) {
                                console.log(error)
                            }
                        }
                    }
                    // 打印被替换实现的所有方法名
                    if (overloads.length > 1) {
                        this.log(className + "." + matchMethod + " 重载 * " + overloads.length);
                    } else {
                        this.log(className + "." + matchMethod)
                    }
                }
            }
        }
    }

    static buildSignature(className, methodName, args) {
        let methodSignature = className + "." + methodName + "(";
        for (let index = 0; index < args.length; index++) {
            let arg = args[index];
            if (typeof (arg) == "object") {
                if (arg == null) {
                    methodSignature += arg + ", ";
                } else {
                    methodSignature += arg.getClass().getName() + ", ";
                }
            } else if (typeof (arg) == "string") {
                methodSignature += "java.lang.String, ";
            }

        }
        return methodSignature.substring(0, methodSignature.length - 2) + ")";
    }

    // 堆栈信息打印
    static printBacktrace(request_key) {
        // 开启堆栈打印
        if (this.backtrace) {
            // 直接打印堆栈
            var stacktrace = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new());
            this.log("Backtrace:");
            this.log(stacktrace);
        } else {
            // 关闭堆栈打印
        }
    }

    /**
     * 1.打印方法执行开始时间
     * 2.打印方法入参值
     * 3.打印堆栈信息
     */
    static printInfoBeforeMethodExecute(signature, args) {
        if (this.depth == 0) {
            console.log()
            console.log("======================= 清晰美观的分割线 =======================")
            console.log()
        }

        // 输出方法执行的开始时间点
        if (this.duration) {
            this.log(new Date().getTime() + " 开始调用：" + signature)
        } else {
            this.log("调用：" + signature)
        }
        // 输出入参值
        let values = ""
        for (let index = 0; index < args.length; index++) {
            let arg = args[index]
            if (typeof (arg) == "object") {
                if (arg == null) {
                    values += "参数" + (index + 1) + ": " + arg + "; "
                } else {
                    values += "参数" + (index + 1) + ": " + args[index].toString() + "; "
                }
            } else {
                values += "参数" + (index + 1) + ": " + arg + "; "
            }
        }
        this.log(values)
        // 打印堆栈
        this.printBacktrace(signature);
        this.depth++;
    }

    /**
     * 1.打印方法返回值
     * 2.打印方法执行结束时间
     */
    static printInfoAfterMethodExecute(signature, result) {
        this.depth--;
        if (typeof (result) == 'object') {
            if (result == null) {
                this.log("返回值：" + result);
            } else {
                this.log("返回值：" + result.toString());
            }
        } else {
            this.log("返回值：" + result);
        }

        // 输出方法执行的结束时间点
        if (this.duration) {
            this.log(new Date().getTime() + " 结束调用：" + signature)
        }
    }

    static log(msg) {
        for (let i = 0; i < this.depth; i++) {
            msg = ("   | " + msg)
        }
        console.log(msg)
    }
}

class iOSMode {
    static include_ios_method = [];
    static backtrace_ios = false
    static duration_ios = false

    static init(include_method, backtrace, duration) {
        this.include_ios_method = include_method;
        this.backtrace_ios = backtrace;
        this.duration_ios = duration;

        console.log("\niOSMode init:")
        console.log("\tinclude_method: " + this.include_ios_method);
        console.log("\tshow_backtrace: " + this.backtrace_ios);
        console.log("\tshow_duration: " + this.duration_ios);

        console.log("\nDump key app paths and metadata:")
        console.log(JSON.stringify(this.appInfo(),null,2))
        console.log("\nContents of Info.plist:")
        console.log(JSON.stringify(this.infoDictionary(),null,2))

        this.traceMethod_iOS();
    }

    static traceMethod_iOS() {
        let apiResolver = new ApiResolver('objc');

        let matches;
        for (let query of this.include_ios_method) {
            matches = apiResolver.enumerateMatches(query).concat(matches);
        }
        matches.pop(null)

        console.log("\n以下方法已被成功替换：")
        for (let match of matches) {
            let name = match['name'];
            console.log(name);
            Interceptor.attach(match['address'], {
                onEnter(args) {
                    iOSMode.printInfoBeforeMethodExecute_iOS(name, iOSMode.getRealArgs(args, name), this.context, this.depth, this.threadId);
                },
                onLeave(result) {
                    iOSMode.printInfoAfterMethodExecute_iOS(name, result, this.depth);
                }
            })
        }
    }

    /**
     * 1.打印方法执行开始时间
     * 2.打印方法入参值
     * 3.打印堆栈信息
     */
    static printInfoBeforeMethodExecute_iOS(name, args, context, depth, threadId) {
        if (depth == 0) {
            console.log()
            console.log("/* TID " + threadId + " */")
        }

        // 输出方法执行的开始时间点
        if (this.duration_ios) {
            this.log_iOS(new Date().getTime() + " 开始调用：" + name, depth)
        } else {
            this.log_iOS("调用：" + name, depth)
        }
        // 输出入参值
        let values = ""
        for (let index = 0; index < args.length; index++) {
            //values += "参数 " + (index + 1) + ": " + new ObjC.Object(arg) + "; "
            this.log_iOS("参数 " + (index + 1) + ": " + this.getPointerValue(args[index]) + "; ", depth);
        }
        //log_iOS(values)

        // 打印堆栈
        this.printBacktrace_iOS(context, depth);
    }

    /**
     * 1.打印方法返回值
     * 2.打印方法执行结束时间
     */
    static printInfoAfterMethodExecute_iOS(name, result, depth) {
        // 输出方法执行的结束时间点
        this.log_iOS("返回值：" + this.getPointerValue(result), depth);
        if (this.duration_ios) {
            this.log_iOS(new Date().getTime() + " 结束调用：" + name, depth)
        }
    }

    static getRealArgs(args, name) {
        let real_args = [];
        if (name.indexOf(":") !== -1) {
            let par = name.split(":");
            par[0] = par[0].split(" ")[1];
            for (var i = 2; i < par.length + 1; i++) {
                real_args.push(args[i])
            }
        }
        return real_args;
    }


    static getPointerValue(pointer) {
        if (Magic.isObjC(pointer)) {
            return JSON.stringify(this.getObjectValue(new ObjC.Object(pointer)));
        } else {
            return pointer.toString();
        }
    }

    static getObjectValue(object){
        let NSDictionary = ObjC.classes.NSDictionary;
        let NSArray = ObjC.classes.NSArray;
        let NSSet = ObjC.classes.NSSet;

        if (object.isKindOfClass_(NSDictionary)) {
            return this.dictFromNSDictionary(object);
        }else if(object.isKindOfClass_(NSArray)){
            return this.arrayFromNSArray(object);
        }else if(object.isKindOfClass_(NSSet)){
            return this.setFromNSSet(object);
        }else {
            return object.toString();
        }
    }

    static dictFromNSDictionary(nsDict) {
        var jsDict = {};
        var keys = nsDict.allKeys();
        var count = keys.count();
        for (var i = 0; i < count; i++) {
            var key = keys.objectAtIndex_(i);
            var value = nsDict.objectForKey_(key);
            jsDict[key.toString()] = this.getObjectValue(value);
        }
        return jsDict;
    }
    
    static arrayFromNSArray(nsArray) {
        var jsArray = [];
        var count = nsArray.count();
        for (var i = 0; i < count; i++) {
            jsArray[i] = this.getObjectValue(nsArray.objectAtIndex_(i));
        }
        return jsArray;
    }

    static setFromNSSet(nsSet){
        return this.arrayFromNSArray(nsSet.allObjects());
    }

    // https://github.com/frida/frida/issues/1531
    static convertNSDictionaryToString(dict) {
        // let NSJSONSerialization = ObjC.classes.NSJSONSerialization
        try {
            let NSJSONSerialization = ObjC.classes.NSJSONSerialization;
            let NSString = ObjC.classes.NSString;

            console.log(dict.$handle + " " + dict.$h + " " + dict.handle)
            console.log(dict.$className);
            let data = NSJSONSerialization.dataWithJSONObject_options_error_(dict, 0, 0);
            // NSUTF8StringEncoding = 4 
            return NSString.alloc().initWithData_encoding_(data, 4)
        } catch (error) {
            console.log(error)
        }

    }

    // 堆栈信息打印
    static printBacktrace_iOS(context, depth) {
        // 开启堆栈打印
        if (this.backtrace_ios) {
            this.log_iOS('Backtrace:' + Thread.backtrace(context,
                Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'), depth);
        } else {
            // 关闭堆栈打印
        }
    }

    static log_iOS(msg, depth) {
        for (let i = 0; i < depth; i++) {
            msg = ("   | " + msg)
        }
        console.log(msg);
    }

    // from https://codeshare.frida.re/@dki/ios-app-info/
    static infoDictionary() {
        if (ObjC.available && "NSBundle" in ObjC.classes) {
            var info = ObjC.classes.NSBundle.mainBundle().infoDictionary();
            return this.dictFromNSDictionary(info);
        }
        return null;
    }
    
    static infoLookup(key) {
        if (ObjC.available && "NSBundle" in ObjC.classes) {
            var info = ObjC.classes.NSBundle.mainBundle().infoDictionary();
            var value = info.objectForKey_(key);
            if (value === null) {
                return value;
            } else if (value.class().toString() === "__NSCFArray") {
                return this.arrayFromNSArray(value);
            } else if (value.class().toString() === "__NSCFDictionary") {
                return this.dictFromNSDictionary(value);
            } else {
                return value.toString();
            }
        }
        return null;
    }
    
    static appInfo() {
        var output = {};
        output["Name"] = this.infoLookup("CFBundleName");
        output["Bundle ID"] = ObjC.classes.NSBundle.mainBundle().bundleIdentifier().toString();
        output["Version"] = this.infoLookup("CFBundleVersion");
        output["Bundle"] = ObjC.classes.NSBundle.mainBundle().bundlePath().toString();
        output["Data"] = ObjC.classes.NSProcessInfo.processInfo().environment().objectForKey_("HOME").toString();
        output["Binary"] = ObjC.classes.NSBundle.mainBundle().executablePath().toString();
        return output;
    }
}

class Magic {
    // 值类型 vs 引用类型
    // The code below is from https://github.com/frida/frida/issues/1064
    static ISA_MASK = ptr('0x0000000ffffffff8');
    static ISA_MAGIC_MASK = ptr('0x000003f000000001');
    static ISA_MAGIC_VALUE = ptr('0x000001a000000001');

    static isObjC(p) {
        var klass = this.getObjCClassPtr(p);
        return !klass.isNull();
    }

    static getObjCClassPtr(p) {
        /*
        * Loosely based on:
        * https://blog.timac.org/2016/1124-testing-if-an-arbitrary-pointer-is-a-valid-objective-c-object/
        */

        if (!this.isReadable(p)) {
            return NULL;
        }
        var isa = p.readPointer();
        var classP = isa;
        if (classP.and(this.ISA_MAGIC_MASK).equals(this.ISA_MAGIC_VALUE)) {
            classP = isa.and(this.ISA_MASK);
        }
        if (this.isReadable(classP)) {
            return classP;
        }
        return NULL;
    }

    static isReadable(p) {
        try {
            p.readU8();
            return true;
        } catch (e) {
            return false;
        }
    }
}


if (Java.available) {
    AndroidMode.init(_include_method, _backtrace, _duration, _spawn);
} else if (ObjC.available) {
    iOSMode.init(_include_method, _backtrace, _duration);
} else {
    console.log("非 Android/iOS 环境，什么也不做")
}
"""

if __name__ == '__main__':
    sys.exit(main())