(function() {
    if (!Element.prototype.matches) {
        Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
    }
    
    if (!Element.prototype.closest) {
        Element.prototype.closest = function(s) {
            var el = this;
            do {
                if (Element.prototype.matches.call(el, s)) return el;
                el = el.parentElement || el.parentNode;
            } while (el !== null && el.nodeType === 1);
            return null;
        };
    }

    if (!Array.from) {
        Array.from = (function () {
            var toStr = Object.prototype.toString;
            var isCallable = function (fn) {
                return typeof fn === 'function' || toStr.call(fn) === '[object Function]';
            };
            var toInteger = function (value) {
                var number = Number(value);
                if (isNaN(number)) { return 0; }
                if (number === 0 || !isFinite(number)) { return number; }
                return (number > 0 ? 1 : -1) * Math.floor(Math.abs(number));
            };
            var maxSafeInteger = Math.pow(2, 53) - 1;
            var toLength = function (value) {
                var len = toInteger(value);
                return Math.min(Math.max(len, 0), maxSafeInteger);
            };

            return function from(arrayLike) {
                var C = this;
                var items = Object(arrayLike);

                if (arrayLike == null) {
                    throw new TypeError('Array.from requires an array-like object - not null or undefined');
                }

                var mapFn = arguments.length > 1 ? arguments[1] : void undefined;
                var T;
                if (typeof mapFn !== 'undefined') {
                    if (!isCallable(mapFn)) {
                        throw new TypeError('Array.from: when provided, the second argument must be a function');
                    }
                    if (arguments.length > 2) {
                        T = arguments[2];
                    }
                }

                var len = toLength(items.length);
                var A = isCallable(C) ? Object(new C(len)) : new Array(len);
                var k = 0;
                var kValue;
                while (k < len) {
                    kValue = items[k];
                    if (mapFn) {
                        A[k] = typeof T === 'undefined' ? mapFn(kValue, k) : mapFn.call(T, kValue, k);
                    } else {
                        A[k] = kValue;
                    }
                    k += 1;
                }
                A.length = len;
                return A;
            };
        }());
    }

    if (window.NodeList && !NodeList.prototype.forEach) {
        NodeList.prototype.forEach = function (callback, thisArg) {
            thisArg = thisArg || window;
            for (var i = 0; i < this.length; i++) {
                callback.call(thisArg, this[i], i, this);
            }
        };
    }

    if (!window.fetch) {
        window.fetch = function(url, options) {
            options = options || {};
            return new Promise(function(resolve, reject) {
                var xhr = new XMLHttpRequest();
                xhr.open(options.method || 'GET', url);
                
                if (options.headers) {
                    for (var header in options.headers) {
                        xhr.setRequestHeader(header, options.headers[header]);
                    }
                }
                
                xhr.onload = function() {
                    resolve({
                        ok: xhr.status >= 200 && xhr.status < 300,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        text: function() { return Promise.resolve(xhr.responseText); },
                        json: function() { return Promise.resolve(JSON.parse(xhr.responseText)); }
                    });
                };
                
                xhr.onerror = function() {
                    reject(new TypeError('Network request failed'));
                };
                
                xhr.send(options.body || null);
            });
        };
    }

    if (typeof Promise !== "function") {
        window.Promise = function(executor) {
            this.state = 'pending';
            this.value = undefined;
            this.onResolvedCallbacks = [];
            this.onRejectedCallbacks = [];
            
            var resolve = (value) => {
                if (this.state === 'pending') {
                    this.state = 'resolved';
                    this.value = value;
                    this.onResolvedCallbacks.forEach(fn => fn());
                }
            };
            
            var reject = (reason) => {
                if (this.state === 'pending') {
                    this.state = 'rejected';
                    this.value = reason;
                    this.onRejectedCallbacks.forEach(fn => fn());
                }
            };
            
            try {
                executor(resolve, reject);
            } catch (e) {
                reject(e);
            }
        };
        
        Promise.prototype.then = function(onFulfilled, onRejected) {
            return new Promise((resolve, reject) => {
                if (this.state === 'pending') {
                    this.onResolvedCallbacks.push(() => {
                        try {
                            var result = onFulfilled(this.value);
                            resolve(result);
                        } catch (e) {
                            reject(e);
                        }
                    });
                    
                    this.onRejectedCallbacks.push(() => {
                        try {
                            var result = onRejected(this.value);
                            resolve(result);
                        } catch (e) {
                            reject(e);
                        }
                    });
                }
                
                if (this.state === 'resolved') {
                    try {
                        var result = onFulfilled(this.value);
                        resolve(result);
                    } catch (e) {
                        reject(e);
                    }
                }
                
                if (this.state === 'rejected') {
                    try {
                        var result = onRejected(this.value);
                        resolve(result);
                    } catch (e) {
                        reject(e);
                    }
                }
            });
        };
    }
})();

window.Compatibility = {
    checkBrowserSupport: function() {
        var unsupported = [];
        
        if (!window.fetch) {
            unsupported.push('fetch API');
        }
        
        if (!window.Promise) {
            unsupported.push('Promise');
        }
        
        if (!Array.from) {
            unsupported.push('Array.from');
        }
        
        if (!Element.prototype.closest) {
            unsupported.push('Element.closest');
        }
        
        if (!NodeList.prototype.forEach) {
            unsupported.push('NodeList.forEach');
        }
        
        return unsupported;
    },
    
    showCompatibilityWarning: function(unsupportedFeatures) {
        var message = '您的浏览器不支持以下功能，可能会影响使用体验：\n\n' + 
                      unsupportedFeatures.join('\n') + 
                      '\n\n建议升级到最新版的现代浏览器（如Chrome、Firefox、Edge等）';
        
        console.warn(message);
        
        var warningDiv = document.createElement('div');
        warningDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: #ffcc00;
            color: #333;
            padding: 10px;
            text-align: center;
            z-index: 9999;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        `;
        warningDiv.innerHTML = `
            <strong>浏览器兼容性警告：</strong> 您的浏览器版本过低，可能无法正常显示页面内容。 
            <a href="#" onclick="this.parentElement.style.display='none';return false;" style="float:right;color:#333;">×</a>
        `;
        
        if (document.body.firstChild) {
            document.body.insertBefore(warningDiv, document.body.firstChild);
        } else {
            document.body.appendChild(warningDiv);
        }
    },
    
    init: function() {
        var unsupported = this.checkBrowserSupport();
        if (unsupported.length > 0) {
            this.showCompatibilityWarning(unsupported);
        }
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.Compatibility.init();
    });
} else {
    window.Compatibility.init();
}