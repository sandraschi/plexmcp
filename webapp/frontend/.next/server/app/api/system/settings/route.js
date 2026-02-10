/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "app/api/system/settings/route";
exports.ids = ["app/api/system/settings/route"];
exports.modules = {

/***/ "(rsc)/./app/api/system/settings/route.ts":
/*!******************************************!*\
  !*** ./app/api/system/settings/route.ts ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   GET: () => (/* binding */ GET),\n/* harmony export */   PATCH: () => (/* binding */ PATCH)\n/* harmony export */ });\n/* harmony import */ var _lib_proxy__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/lib/proxy */ \"(rsc)/./lib/proxy.ts\");\n\nconst BACKEND_URL = (process.env.API_URL || \"http://127.0.0.1:10740\" || 0).replace(\"localhost\", \"127.0.0.1\");\nasync function GET(request) {\n    try {\n        return await (0,_lib_proxy__WEBPACK_IMPORTED_MODULE_0__.proxyGet)(\"/api/system/settings\");\n    } catch  {\n        return new Response(null, {\n            status: 502\n        });\n    }\n}\nasync function PATCH(request) {\n    try {\n        const body = await request.json();\n        const res = await fetch(`${BACKEND_URL}/api/system/settings`, {\n            method: \"PATCH\",\n            headers: {\n                \"Content-Type\": \"application/json\"\n            },\n            body: JSON.stringify(body)\n        });\n        const data = await res.json();\n        if (!res.ok) return new Response(JSON.stringify(data), {\n            status: res.status\n        });\n        return new Response(JSON.stringify(data), {\n            status: 200,\n            headers: {\n                \"Content-Type\": \"application/json\"\n            }\n        });\n    } catch  {\n        return new Response(null, {\n            status: 502\n        });\n    }\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9hcHAvYXBpL3N5c3RlbS9zZXR0aW5ncy9yb3V0ZS50cyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFDdUM7QUFFdkMsTUFBTUMsY0FBYyxDQUNsQkMsUUFBUUMsR0FBRyxDQUFDQyxPQUFPLElBQ25CRix3QkFBK0IsSUFDL0IsQ0FBdUIsRUFDdkJJLE9BQU8sQ0FBQyxhQUFhO0FBRWhCLGVBQWVDLElBQUlDLE9BQW9CO0lBQzVDLElBQUk7UUFDRixPQUFPLE1BQU1SLG9EQUFRQSxDQUFDO0lBQ3hCLEVBQUUsT0FBTTtRQUNOLE9BQU8sSUFBSVMsU0FBUyxNQUFNO1lBQUVDLFFBQVE7UUFBSTtJQUMxQztBQUNGO0FBRU8sZUFBZUMsTUFBTUgsT0FBb0I7SUFDOUMsSUFBSTtRQUNGLE1BQU1JLE9BQU8sTUFBTUosUUFBUUssSUFBSTtRQUMvQixNQUFNQyxNQUFNLE1BQU1DLE1BQU0sR0FBR2QsWUFBWSxvQkFBb0IsQ0FBQyxFQUFFO1lBQzVEZSxRQUFRO1lBQ1JDLFNBQVM7Z0JBQUUsZ0JBQWdCO1lBQW1CO1lBQzlDTCxNQUFNTSxLQUFLQyxTQUFTLENBQUNQO1FBQ3ZCO1FBQ0EsTUFBTVEsT0FBTyxNQUFNTixJQUFJRCxJQUFJO1FBQzNCLElBQUksQ0FBQ0MsSUFBSU8sRUFBRSxFQUFFLE9BQU8sSUFBSVosU0FBU1MsS0FBS0MsU0FBUyxDQUFDQyxPQUFPO1lBQUVWLFFBQVFJLElBQUlKLE1BQU07UUFBQztRQUM1RSxPQUFPLElBQUlELFNBQVNTLEtBQUtDLFNBQVMsQ0FBQ0MsT0FBTztZQUN4Q1YsUUFBUTtZQUNSTyxTQUFTO2dCQUFFLGdCQUFnQjtZQUFtQjtRQUNoRDtJQUNGLEVBQUUsT0FBTTtRQUNOLE9BQU8sSUFBSVIsU0FBUyxNQUFNO1lBQUVDLFFBQVE7UUFBSTtJQUMxQztBQUNGIiwic291cmNlcyI6WyJEOlxcRGV2XFxyZXBvc1xccGxleC1tY3BcXHdlYmFwcFxcZnJvbnRlbmRcXGFwcFxcYXBpXFxzeXN0ZW1cXHNldHRpbmdzXFxyb3V0ZS50cyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBOZXh0UmVxdWVzdCB9IGZyb20gXCJuZXh0L3NlcnZlclwiO1xyXG5pbXBvcnQgeyBwcm94eUdldCB9IGZyb20gXCJAL2xpYi9wcm94eVwiO1xyXG5cclxuY29uc3QgQkFDS0VORF9VUkwgPSAoXHJcbiAgcHJvY2Vzcy5lbnYuQVBJX1VSTCB8fFxyXG4gIHByb2Nlc3MuZW52Lk5FWFRfUFVCTElDX0FQSV9VUkwgfHxcclxuICBcImh0dHA6Ly8xMjcuMC4wLjE6MTA3NDBcIlxyXG4pLnJlcGxhY2UoXCJsb2NhbGhvc3RcIiwgXCIxMjcuMC4wLjFcIik7XHJcblxyXG5leHBvcnQgYXN5bmMgZnVuY3Rpb24gR0VUKHJlcXVlc3Q6IE5leHRSZXF1ZXN0KSB7XHJcbiAgdHJ5IHtcclxuICAgIHJldHVybiBhd2FpdCBwcm94eUdldChcIi9hcGkvc3lzdGVtL3NldHRpbmdzXCIpO1xyXG4gIH0gY2F0Y2gge1xyXG4gICAgcmV0dXJuIG5ldyBSZXNwb25zZShudWxsLCB7IHN0YXR1czogNTAyIH0pO1xyXG4gIH1cclxufVxyXG5cclxuZXhwb3J0IGFzeW5jIGZ1bmN0aW9uIFBBVENIKHJlcXVlc3Q6IE5leHRSZXF1ZXN0KSB7XHJcbiAgdHJ5IHtcclxuICAgIGNvbnN0IGJvZHkgPSBhd2FpdCByZXF1ZXN0Lmpzb24oKTtcclxuICAgIGNvbnN0IHJlcyA9IGF3YWl0IGZldGNoKGAke0JBQ0tFTkRfVVJMfS9hcGkvc3lzdGVtL3NldHRpbmdzYCwge1xyXG4gICAgICBtZXRob2Q6IFwiUEFUQ0hcIixcclxuICAgICAgaGVhZGVyczogeyBcIkNvbnRlbnQtVHlwZVwiOiBcImFwcGxpY2F0aW9uL2pzb25cIiB9LFxyXG4gICAgICBib2R5OiBKU09OLnN0cmluZ2lmeShib2R5KSxcclxuICAgIH0pO1xyXG4gICAgY29uc3QgZGF0YSA9IGF3YWl0IHJlcy5qc29uKCk7XHJcbiAgICBpZiAoIXJlcy5vaykgcmV0dXJuIG5ldyBSZXNwb25zZShKU09OLnN0cmluZ2lmeShkYXRhKSwgeyBzdGF0dXM6IHJlcy5zdGF0dXMgfSk7XHJcbiAgICByZXR1cm4gbmV3IFJlc3BvbnNlKEpTT04uc3RyaW5naWZ5KGRhdGEpLCB7XHJcbiAgICAgIHN0YXR1czogMjAwLFxyXG4gICAgICBoZWFkZXJzOiB7IFwiQ29udGVudC1UeXBlXCI6IFwiYXBwbGljYXRpb24vanNvblwiIH0sXHJcbiAgICB9KTtcclxuICB9IGNhdGNoIHtcclxuICAgIHJldHVybiBuZXcgUmVzcG9uc2UobnVsbCwgeyBzdGF0dXM6IDUwMiB9KTtcclxuICB9XHJcbn1cclxuIl0sIm5hbWVzIjpbInByb3h5R2V0IiwiQkFDS0VORF9VUkwiLCJwcm9jZXNzIiwiZW52IiwiQVBJX1VSTCIsIk5FWFRfUFVCTElDX0FQSV9VUkwiLCJyZXBsYWNlIiwiR0VUIiwicmVxdWVzdCIsIlJlc3BvbnNlIiwic3RhdHVzIiwiUEFUQ0giLCJib2R5IiwianNvbiIsInJlcyIsImZldGNoIiwibWV0aG9kIiwiaGVhZGVycyIsIkpTT04iLCJzdHJpbmdpZnkiLCJkYXRhIiwib2siXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///(rsc)/./app/api/system/settings/route.ts\n");

/***/ }),

/***/ "(rsc)/./lib/proxy.ts":
/*!**********************!*\
  !*** ./lib/proxy.ts ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   proxyGet: () => (/* binding */ proxyGet)\n/* harmony export */ });\n/* harmony import */ var next_server__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/server */ \"(rsc)/./node_modules/next/dist/api/server.js\");\n\nconst BACKEND_URL = (process.env.API_URL || \"http://127.0.0.1:10740\" || 0).replace(\"localhost\", \"127.0.0.1\");\nconst PROXY_TIMEOUT_MS = 15000;\nasync function proxyGet(path, searchParams) {\n    const url = searchParams ? `${BACKEND_URL}${path}?${typeof searchParams === \"string\" ? searchParams : searchParams.toString()}` : `${BACKEND_URL}${path}`;\n    const controller = new AbortController();\n    const t = setTimeout(()=>controller.abort(), PROXY_TIMEOUT_MS);\n    try {\n        const res = await fetch(url, {\n            signal: controller.signal,\n            cache: \"no-store\"\n        });\n        if (!res.ok) {\n            let errBody = {\n                error: `Backend returned ${res.status}`\n            };\n            try {\n                const text = await res.text();\n                if (text) {\n                    try {\n                        errBody = JSON.parse(text);\n                    } catch  {\n                        errBody = {\n                            error: text.slice(0, 500)\n                        };\n                    }\n                }\n            } catch  {\n            /* ignore */ }\n            return next_server__WEBPACK_IMPORTED_MODULE_0__.NextResponse.json(errBody, {\n                status: res.status\n            });\n        }\n        return new next_server__WEBPACK_IMPORTED_MODULE_0__.NextResponse(res.body, {\n            status: res.status,\n            headers: {\n                \"Content-Type\": res.headers.get(\"content-type\") ?? \"application/json\"\n            }\n        });\n    } finally{\n        clearTimeout(t);\n    }\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9saWIvcHJveHkudHMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBMkM7QUFFM0MsTUFBTUMsY0FBYyxDQUNsQkMsUUFBUUMsR0FBRyxDQUFDQyxPQUFPLElBQ25CRix3QkFBK0IsSUFDL0IsQ0FBdUIsRUFDdkJJLE9BQU8sQ0FBQyxhQUFhO0FBQ3ZCLE1BQU1DLG1CQUFtQjtBQUVsQixlQUFlQyxTQUNwQkMsSUFBWSxFQUNaQyxZQUF1QztJQUV2QyxNQUFNQyxNQUFNRCxlQUNSLEdBQUdULGNBQWNRLEtBQUssQ0FBQyxFQUFFLE9BQU9DLGlCQUFpQixXQUFXQSxlQUFlQSxhQUFhRSxRQUFRLElBQUksR0FDcEcsR0FBR1gsY0FBY1EsTUFBTTtJQUMzQixNQUFNSSxhQUFhLElBQUlDO0lBQ3ZCLE1BQU1DLElBQUlDLFdBQVcsSUFBTUgsV0FBV0ksS0FBSyxJQUFJVjtJQUMvQyxJQUFJO1FBQ0YsTUFBTVcsTUFBTSxNQUFNQyxNQUFNUixLQUFLO1lBQzNCUyxRQUFRUCxXQUFXTyxNQUFNO1lBQ3pCQyxPQUFPO1FBQ1Q7UUFDQSxJQUFJLENBQUNILElBQUlJLEVBQUUsRUFBRTtZQUNYLElBQUlDLFVBQStDO2dCQUNqREMsT0FBTyxDQUFDLGlCQUFpQixFQUFFTixJQUFJTyxNQUFNLEVBQUU7WUFDekM7WUFDQSxJQUFJO2dCQUNGLE1BQU1DLE9BQU8sTUFBTVIsSUFBSVEsSUFBSTtnQkFDM0IsSUFBSUEsTUFBTTtvQkFDUixJQUFJO3dCQUNGSCxVQUFVSSxLQUFLQyxLQUFLLENBQUNGO29CQUN2QixFQUFFLE9BQU07d0JBQ05ILFVBQVU7NEJBQUVDLE9BQU9FLEtBQUtHLEtBQUssQ0FBQyxHQUFHO3dCQUFLO29CQUN4QztnQkFDRjtZQUNGLEVBQUUsT0FBTTtZQUNOLFVBQVUsR0FDWjtZQUNBLE9BQU83QixxREFBWUEsQ0FBQzhCLElBQUksQ0FBQ1AsU0FBUztnQkFBRUUsUUFBUVAsSUFBSU8sTUFBTTtZQUFDO1FBQ3pEO1FBQ0EsT0FBTyxJQUFJekIscURBQVlBLENBQUNrQixJQUFJYSxJQUFJLEVBQUU7WUFDaENOLFFBQVFQLElBQUlPLE1BQU07WUFDbEJPLFNBQVM7Z0JBQUUsZ0JBQWdCZCxJQUFJYyxPQUFPLENBQUNDLEdBQUcsQ0FBQyxtQkFBbUI7WUFBbUI7UUFDbkY7SUFDRixTQUFVO1FBQ1JDLGFBQWFuQjtJQUNmO0FBQ0YiLCJzb3VyY2VzIjpbIkQ6XFxEZXZcXHJlcG9zXFxwbGV4LW1jcFxcd2ViYXBwXFxmcm9udGVuZFxcbGliXFxwcm94eS50cyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBOZXh0UmVzcG9uc2UgfSBmcm9tIFwibmV4dC9zZXJ2ZXJcIjtcclxuXHJcbmNvbnN0IEJBQ0tFTkRfVVJMID0gKFxyXG4gIHByb2Nlc3MuZW52LkFQSV9VUkwgfHxcclxuICBwcm9jZXNzLmVudi5ORVhUX1BVQkxJQ19BUElfVVJMIHx8XHJcbiAgXCJodHRwOi8vMTI3LjAuMC4xOjEwNzQwXCJcclxuKS5yZXBsYWNlKFwibG9jYWxob3N0XCIsIFwiMTI3LjAuMC4xXCIpO1xyXG5jb25zdCBQUk9YWV9USU1FT1VUX01TID0gMTUwMDA7XHJcblxyXG5leHBvcnQgYXN5bmMgZnVuY3Rpb24gcHJveHlHZXQoXHJcbiAgcGF0aDogc3RyaW5nLFxyXG4gIHNlYXJjaFBhcmFtcz86IFVSTFNlYXJjaFBhcmFtcyB8IHN0cmluZ1xyXG4pOiBQcm9taXNlPE5leHRSZXNwb25zZT4ge1xyXG4gIGNvbnN0IHVybCA9IHNlYXJjaFBhcmFtc1xyXG4gICAgPyBgJHtCQUNLRU5EX1VSTH0ke3BhdGh9PyR7dHlwZW9mIHNlYXJjaFBhcmFtcyA9PT0gXCJzdHJpbmdcIiA/IHNlYXJjaFBhcmFtcyA6IHNlYXJjaFBhcmFtcy50b1N0cmluZygpfWBcclxuICAgIDogYCR7QkFDS0VORF9VUkx9JHtwYXRofWA7XHJcbiAgY29uc3QgY29udHJvbGxlciA9IG5ldyBBYm9ydENvbnRyb2xsZXIoKTtcclxuICBjb25zdCB0ID0gc2V0VGltZW91dCgoKSA9PiBjb250cm9sbGVyLmFib3J0KCksIFBST1hZX1RJTUVPVVRfTVMpO1xyXG4gIHRyeSB7XHJcbiAgICBjb25zdCByZXMgPSBhd2FpdCBmZXRjaCh1cmwsIHtcclxuICAgICAgc2lnbmFsOiBjb250cm9sbGVyLnNpZ25hbCxcclxuICAgICAgY2FjaGU6IFwibm8tc3RvcmVcIixcclxuICAgIH0pO1xyXG4gICAgaWYgKCFyZXMub2spIHtcclxuICAgICAgbGV0IGVyckJvZHk6IHsgZXJyb3I/OiBzdHJpbmc7IGRldGFpbD86IHN0cmluZyB9ID0ge1xyXG4gICAgICAgIGVycm9yOiBgQmFja2VuZCByZXR1cm5lZCAke3Jlcy5zdGF0dXN9YCxcclxuICAgICAgfTtcclxuICAgICAgdHJ5IHtcclxuICAgICAgICBjb25zdCB0ZXh0ID0gYXdhaXQgcmVzLnRleHQoKTtcclxuICAgICAgICBpZiAodGV4dCkge1xyXG4gICAgICAgICAgdHJ5IHtcclxuICAgICAgICAgICAgZXJyQm9keSA9IEpTT04ucGFyc2UodGV4dCk7XHJcbiAgICAgICAgICB9IGNhdGNoIHtcclxuICAgICAgICAgICAgZXJyQm9keSA9IHsgZXJyb3I6IHRleHQuc2xpY2UoMCwgNTAwKSB9O1xyXG4gICAgICAgICAgfVxyXG4gICAgICAgIH1cclxuICAgICAgfSBjYXRjaCB7XHJcbiAgICAgICAgLyogaWdub3JlICovXHJcbiAgICAgIH1cclxuICAgICAgcmV0dXJuIE5leHRSZXNwb25zZS5qc29uKGVyckJvZHksIHsgc3RhdHVzOiByZXMuc3RhdHVzIH0pO1xyXG4gICAgfVxyXG4gICAgcmV0dXJuIG5ldyBOZXh0UmVzcG9uc2UocmVzLmJvZHksIHtcclxuICAgICAgc3RhdHVzOiByZXMuc3RhdHVzLFxyXG4gICAgICBoZWFkZXJzOiB7IFwiQ29udGVudC1UeXBlXCI6IHJlcy5oZWFkZXJzLmdldChcImNvbnRlbnQtdHlwZVwiKSA/PyBcImFwcGxpY2F0aW9uL2pzb25cIiB9LFxyXG4gICAgfSk7XHJcbiAgfSBmaW5hbGx5IHtcclxuICAgIGNsZWFyVGltZW91dCh0KTtcclxuICB9XHJcbn1cclxuIl0sIm5hbWVzIjpbIk5leHRSZXNwb25zZSIsIkJBQ0tFTkRfVVJMIiwicHJvY2VzcyIsImVudiIsIkFQSV9VUkwiLCJORVhUX1BVQkxJQ19BUElfVVJMIiwicmVwbGFjZSIsIlBST1hZX1RJTUVPVVRfTVMiLCJwcm94eUdldCIsInBhdGgiLCJzZWFyY2hQYXJhbXMiLCJ1cmwiLCJ0b1N0cmluZyIsImNvbnRyb2xsZXIiLCJBYm9ydENvbnRyb2xsZXIiLCJ0Iiwic2V0VGltZW91dCIsImFib3J0IiwicmVzIiwiZmV0Y2giLCJzaWduYWwiLCJjYWNoZSIsIm9rIiwiZXJyQm9keSIsImVycm9yIiwic3RhdHVzIiwidGV4dCIsIkpTT04iLCJwYXJzZSIsInNsaWNlIiwianNvbiIsImJvZHkiLCJoZWFkZXJzIiwiZ2V0IiwiY2xlYXJUaW1lb3V0Il0sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./lib/proxy.ts\n");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fsystem%2Fsettings%2Froute&page=%2Fapi%2Fsystem%2Fsettings%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fsystem%2Fsettings%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!":
/*!*************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fsystem%2Fsettings%2Froute&page=%2Fapi%2Fsystem%2Fsettings%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fsystem%2Fsettings%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D! ***!
  \*************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   patchFetch: () => (/* binding */ patchFetch),\n/* harmony export */   routeModule: () => (/* binding */ routeModule),\n/* harmony export */   serverHooks: () => (/* binding */ serverHooks),\n/* harmony export */   workAsyncStorage: () => (/* binding */ workAsyncStorage),\n/* harmony export */   workUnitAsyncStorage: () => (/* binding */ workUnitAsyncStorage)\n/* harmony export */ });\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/dist/server/route-modules/app-route/module.compiled */ \"(rsc)/./node_modules/next/dist/server/route-modules/app-route/module.compiled.js\");\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! next/dist/server/route-kind */ \"(rsc)/./node_modules/next/dist/server/route-kind.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! next/dist/server/lib/patch-fetch */ \"(rsc)/./node_modules/next/dist/server/lib/patch-fetch.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var D_Dev_repos_plex_mcp_webapp_frontend_app_api_system_settings_route_ts__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app/api/system/settings/route.ts */ \"(rsc)/./app/api/system/settings/route.ts\");\n\n\n\n\n// We inject the nextConfigOutput here so that we can use them in the route\n// module.\nconst nextConfigOutput = \"standalone\"\nconst routeModule = new next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__.AppRouteRouteModule({\n    definition: {\n        kind: next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__.RouteKind.APP_ROUTE,\n        page: \"/api/system/settings/route\",\n        pathname: \"/api/system/settings\",\n        filename: \"route\",\n        bundlePath: \"app/api/system/settings/route\"\n    },\n    resolvedPagePath: \"D:\\\\Dev\\\\repos\\\\plex-mcp\\\\webapp\\\\frontend\\\\app\\\\api\\\\system\\\\settings\\\\route.ts\",\n    nextConfigOutput,\n    userland: D_Dev_repos_plex_mcp_webapp_frontend_app_api_system_settings_route_ts__WEBPACK_IMPORTED_MODULE_3__\n});\n// Pull out the exports that we need to expose from the module. This should\n// be eliminated when we've moved the other routes to the new format. These\n// are used to hook into the route.\nconst { workAsyncStorage, workUnitAsyncStorage, serverHooks } = routeModule;\nfunction patchFetch() {\n    return (0,next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__.patchFetch)({\n        workAsyncStorage,\n        workUnitAsyncStorage\n    });\n}\n\n\n//# sourceMappingURL=app-route.js.map//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9ub2RlX21vZHVsZXMvbmV4dC9kaXN0L2J1aWxkL3dlYnBhY2svbG9hZGVycy9uZXh0LWFwcC1sb2FkZXIvaW5kZXguanM/bmFtZT1hcHAlMkZhcGklMkZzeXN0ZW0lMkZzZXR0aW5ncyUyRnJvdXRlJnBhZ2U9JTJGYXBpJTJGc3lzdGVtJTJGc2V0dGluZ3MlMkZyb3V0ZSZhcHBQYXRocz0mcGFnZVBhdGg9cHJpdmF0ZS1uZXh0LWFwcC1kaXIlMkZhcGklMkZzeXN0ZW0lMkZzZXR0aW5ncyUyRnJvdXRlLnRzJmFwcERpcj1EJTNBJTVDRGV2JTVDcmVwb3MlNUNwbGV4LW1jcCU1Q3dlYmFwcCU1Q2Zyb250ZW5kJTVDYXBwJnBhZ2VFeHRlbnNpb25zPXRzeCZwYWdlRXh0ZW5zaW9ucz10cyZwYWdlRXh0ZW5zaW9ucz1qc3gmcGFnZUV4dGVuc2lvbnM9anMmcm9vdERpcj1EJTNBJTVDRGV2JTVDcmVwb3MlNUNwbGV4LW1jcCU1Q3dlYmFwcCU1Q2Zyb250ZW5kJmlzRGV2PXRydWUmdHNjb25maWdQYXRoPXRzY29uZmlnLmpzb24mYmFzZVBhdGg9JmFzc2V0UHJlZml4PSZuZXh0Q29uZmlnT3V0cHV0PXN0YW5kYWxvbmUmcHJlZmVycmVkUmVnaW9uPSZtaWRkbGV3YXJlQ29uZmlnPWUzMCUzRCEiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7Ozs7QUFBK0Y7QUFDdkM7QUFDcUI7QUFDZ0M7QUFDN0c7QUFDQTtBQUNBO0FBQ0Esd0JBQXdCLHlHQUFtQjtBQUMzQztBQUNBLGNBQWMsa0VBQVM7QUFDdkI7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBLFlBQVk7QUFDWixDQUFDO0FBQ0Q7QUFDQTtBQUNBO0FBQ0EsUUFBUSxzREFBc0Q7QUFDOUQ7QUFDQSxXQUFXLDRFQUFXO0FBQ3RCO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDMEY7O0FBRTFGIiwic291cmNlcyI6WyIiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgQXBwUm91dGVSb3V0ZU1vZHVsZSB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL3JvdXRlLW1vZHVsZXMvYXBwLXJvdXRlL21vZHVsZS5jb21waWxlZFwiO1xuaW1wb3J0IHsgUm91dGVLaW5kIH0gZnJvbSBcIm5leHQvZGlzdC9zZXJ2ZXIvcm91dGUta2luZFwiO1xuaW1wb3J0IHsgcGF0Y2hGZXRjaCBhcyBfcGF0Y2hGZXRjaCB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL2xpYi9wYXRjaC1mZXRjaFwiO1xuaW1wb3J0ICogYXMgdXNlcmxhbmQgZnJvbSBcIkQ6XFxcXERldlxcXFxyZXBvc1xcXFxwbGV4LW1jcFxcXFx3ZWJhcHBcXFxcZnJvbnRlbmRcXFxcYXBwXFxcXGFwaVxcXFxzeXN0ZW1cXFxcc2V0dGluZ3NcXFxccm91dGUudHNcIjtcbi8vIFdlIGluamVjdCB0aGUgbmV4dENvbmZpZ091dHB1dCBoZXJlIHNvIHRoYXQgd2UgY2FuIHVzZSB0aGVtIGluIHRoZSByb3V0ZVxuLy8gbW9kdWxlLlxuY29uc3QgbmV4dENvbmZpZ091dHB1dCA9IFwic3RhbmRhbG9uZVwiXG5jb25zdCByb3V0ZU1vZHVsZSA9IG5ldyBBcHBSb3V0ZVJvdXRlTW9kdWxlKHtcbiAgICBkZWZpbml0aW9uOiB7XG4gICAgICAgIGtpbmQ6IFJvdXRlS2luZC5BUFBfUk9VVEUsXG4gICAgICAgIHBhZ2U6IFwiL2FwaS9zeXN0ZW0vc2V0dGluZ3Mvcm91dGVcIixcbiAgICAgICAgcGF0aG5hbWU6IFwiL2FwaS9zeXN0ZW0vc2V0dGluZ3NcIixcbiAgICAgICAgZmlsZW5hbWU6IFwicm91dGVcIixcbiAgICAgICAgYnVuZGxlUGF0aDogXCJhcHAvYXBpL3N5c3RlbS9zZXR0aW5ncy9yb3V0ZVwiXG4gICAgfSxcbiAgICByZXNvbHZlZFBhZ2VQYXRoOiBcIkQ6XFxcXERldlxcXFxyZXBvc1xcXFxwbGV4LW1jcFxcXFx3ZWJhcHBcXFxcZnJvbnRlbmRcXFxcYXBwXFxcXGFwaVxcXFxzeXN0ZW1cXFxcc2V0dGluZ3NcXFxccm91dGUudHNcIixcbiAgICBuZXh0Q29uZmlnT3V0cHV0LFxuICAgIHVzZXJsYW5kXG59KTtcbi8vIFB1bGwgb3V0IHRoZSBleHBvcnRzIHRoYXQgd2UgbmVlZCB0byBleHBvc2UgZnJvbSB0aGUgbW9kdWxlLiBUaGlzIHNob3VsZFxuLy8gYmUgZWxpbWluYXRlZCB3aGVuIHdlJ3ZlIG1vdmVkIHRoZSBvdGhlciByb3V0ZXMgdG8gdGhlIG5ldyBmb3JtYXQuIFRoZXNlXG4vLyBhcmUgdXNlZCB0byBob29rIGludG8gdGhlIHJvdXRlLlxuY29uc3QgeyB3b3JrQXN5bmNTdG9yYWdlLCB3b3JrVW5pdEFzeW5jU3RvcmFnZSwgc2VydmVySG9va3MgfSA9IHJvdXRlTW9kdWxlO1xuZnVuY3Rpb24gcGF0Y2hGZXRjaCgpIHtcbiAgICByZXR1cm4gX3BhdGNoRmV0Y2goe1xuICAgICAgICB3b3JrQXN5bmNTdG9yYWdlLFxuICAgICAgICB3b3JrVW5pdEFzeW5jU3RvcmFnZVxuICAgIH0pO1xufVxuZXhwb3J0IHsgcm91dGVNb2R1bGUsIHdvcmtBc3luY1N0b3JhZ2UsIHdvcmtVbml0QXN5bmNTdG9yYWdlLCBzZXJ2ZXJIb29rcywgcGF0Y2hGZXRjaCwgIH07XG5cbi8vIyBzb3VyY2VNYXBwaW5nVVJMPWFwcC1yb3V0ZS5qcy5tYXAiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fsystem%2Fsettings%2Froute&page=%2Fapi%2Fsystem%2Fsettings%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fsystem%2Fsettings%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!\n");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true!":
/*!******************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true! ***!
  \******************************************************************************************************/
/***/ (() => {



/***/ }),

/***/ "(ssr)/./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true!":
/*!******************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true! ***!
  \******************************************************************************************************/
/***/ (() => {



/***/ }),

/***/ "../app-render/after-task-async-storage.external":
/*!***********************************************************************************!*\
  !*** external "next/dist/server/app-render/after-task-async-storage.external.js" ***!
  \***********************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/server/app-render/after-task-async-storage.external.js");

/***/ }),

/***/ "../app-render/work-async-storage.external":
/*!*****************************************************************************!*\
  !*** external "next/dist/server/app-render/work-async-storage.external.js" ***!
  \*****************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/server/app-render/work-async-storage.external.js");

/***/ }),

/***/ "./work-unit-async-storage.external":
/*!**********************************************************************************!*\
  !*** external "next/dist/server/app-render/work-unit-async-storage.external.js" ***!
  \**********************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/server/app-render/work-unit-async-storage.external.js");

/***/ }),

/***/ "next/dist/compiled/next-server/app-page.runtime.dev.js":
/*!*************************************************************************!*\
  !*** external "next/dist/compiled/next-server/app-page.runtime.dev.js" ***!
  \*************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/compiled/next-server/app-page.runtime.dev.js");

/***/ }),

/***/ "next/dist/compiled/next-server/app-route.runtime.dev.js":
/*!**************************************************************************!*\
  !*** external "next/dist/compiled/next-server/app-route.runtime.dev.js" ***!
  \**************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/compiled/next-server/app-route.runtime.dev.js");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../../../../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/next"], () => (__webpack_exec__("(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fsystem%2Fsettings%2Froute&page=%2Fapi%2Fsystem%2Fsettings%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fsystem%2Fsettings%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!")));
module.exports = __webpack_exports__;

})();