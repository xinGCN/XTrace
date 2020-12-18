(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";

Java.perform(function () {
  var String = Java.use("java.lang.String");
  var TextView = Java.use("android.widget.TextView");

  TextView.setText.overload('java.lang.CharSequence', 'android.widget.TextView$BufferType', 'boolean', 'int').implementation = function (text, type, notifyBefore, oldlen) {
    console.log("setText: " + text);
    this.setText(String.$new(String.replaceAll.call(text, "\\w", "7")), type, notifyBefore, oldlen);
  };

  TextView.setHint.overload('java.lang.CharSequence').implementation = function (hint) {
    console.log("setHint: " + hint);
    this.setHint(String.$new(String.replaceAll.call(hint, "\\w", "7")));
  }; // var GLES20Canvas = Java.use("android.view.GLES20Canvas")
  // GLES20Canvas.drawText.implementation = function(args){
  //     console.log("drawText: " + args[0])
  //     this.drawText(args);
  // }

});

},{}]},{},[1])
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJhZ2VudC9zZXZlbi50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTs7O0FDQUEsSUFBSSxDQUFDLE9BQUwsQ0FBYSxZQUFBO0FBQ1QsTUFBSSxNQUFNLEdBQUcsSUFBSSxDQUFDLEdBQUwsQ0FBUyxrQkFBVCxDQUFiO0FBRUEsTUFBSSxRQUFRLEdBQUcsSUFBSSxDQUFDLEdBQUwsQ0FBUyx5QkFBVCxDQUFmOztBQUNBLEVBQUEsUUFBUSxDQUFDLE9BQVQsQ0FBaUIsUUFBakIsQ0FBMEIsd0JBQTFCLEVBQW9ELG9DQUFwRCxFQUEwRixTQUExRixFQUFxRyxLQUFyRyxFQUE0RyxjQUE1RyxHQUE2SCxVQUFTLElBQVQsRUFBZSxJQUFmLEVBQXFCLFlBQXJCLEVBQW1DLE1BQW5DLEVBQXlDO0FBQ2xLLElBQUEsT0FBTyxDQUFDLEdBQVIsQ0FBWSxjQUFjLElBQTFCO0FBQ0EsU0FBSyxPQUFMLENBQWEsTUFBTSxDQUFDLElBQVAsQ0FBWSxNQUFNLENBQUMsVUFBUCxDQUFrQixJQUFsQixDQUF1QixJQUF2QixFQUE0QixLQUE1QixFQUFrQyxHQUFsQyxDQUFaLENBQWIsRUFBa0UsSUFBbEUsRUFBdUUsWUFBdkUsRUFBb0YsTUFBcEY7QUFDSCxHQUhEOztBQUlBLEVBQUEsUUFBUSxDQUFDLE9BQVQsQ0FBaUIsUUFBakIsQ0FBMEIsd0JBQTFCLEVBQW9ELGNBQXBELEdBQXFFLFVBQVMsSUFBVCxFQUFhO0FBQzlFLElBQUEsT0FBTyxDQUFDLEdBQVIsQ0FBWSxjQUFjLElBQTFCO0FBQ0EsU0FBSyxPQUFMLENBQWEsTUFBTSxDQUFDLElBQVAsQ0FBWSxNQUFNLENBQUMsVUFBUCxDQUFrQixJQUFsQixDQUF1QixJQUF2QixFQUE0QixLQUE1QixFQUFrQyxHQUFsQyxDQUFaLENBQWI7QUFDSCxHQUhELENBUlMsQ0FhVDtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUNILENBbEJEIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIifQ==
