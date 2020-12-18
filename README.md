# XTrace
Trace Java or OBJC methods with options that show method entry, return value, print stack, and method execution time.Base on [frida](https://github.com/frida/frida).

# Install 
All you need to do is:

```
pip3 install git+https://github.com/xinGCN/XTrace.git
```
# Usage
1. select a tracing mode, e.g. spawn(-s), attach(-a), attach frontmost(-F).
2. declare the method you want to trace with the -i option.
3. select whether you want to print stack with the -b option or print method execution time with the -d option.

find more by execute the following terminal command
```
xtrace -h
```
# Description
| LANGUAGE | OPTION VALUE | DESCRIPTION |
|  :----:  |  :----  | :----  |
|  ObjC  | -i "-[SensorsAnalyticsSDK track:]"  | Matches instance method named 'track:', ONLY in class SensorsAnalyticsSDK |
|  ObjC  | -i "-[Sensors* track*]"  | Matches all instance methods begin with 'track' in its name, in All classes begins with 'Sensors' in its name|
|  Java  | -i "\*!track"  | Matches method named 'track' in All classes |
|  Java  | -i "\*.SensorsDataAPI!\*track\*"  | Matches all methods with 'track' in its name, in All classes named 'SensorsDataAPI' |

# Uninstall
try:

```
pip3 uninstall xtrace
```
