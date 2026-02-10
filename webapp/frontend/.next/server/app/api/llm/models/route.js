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
exports.id = "app/api/llm/models/route";
exports.ids = ["app/api/llm/models/route"];
exports.modules = {

/***/ "(rsc)/./app/api/llm/models/route.ts":
/*!*************************************!*\
  !*** ./app/api/llm/models/route.ts ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   GET: () => (/* binding */ GET)\n/* harmony export */ });\n/* harmony import */ var _lib_proxy__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/lib/proxy */ \"(rsc)/./lib/proxy.ts\");\n\nasync function GET(request) {\n    try {\n        const { searchParams } = new URL(request.url);\n        return await (0,_lib_proxy__WEBPACK_IMPORTED_MODULE_0__.proxyGet)(\"/api/llm/models\", searchParams);\n    } catch  {\n        return new Response(null, {\n            status: 502\n        });\n    }\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9hcHAvYXBpL2xsbS9tb2RlbHMvcm91dGUudHMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFDdUM7QUFFaEMsZUFBZUMsSUFBSUMsT0FBb0I7SUFDNUMsSUFBSTtRQUNGLE1BQU0sRUFBRUMsWUFBWSxFQUFFLEdBQUcsSUFBSUMsSUFBSUYsUUFBUUcsR0FBRztRQUM1QyxPQUFPLE1BQU1MLG9EQUFRQSxDQUFDLG1CQUFtQkc7SUFDM0MsRUFBRSxPQUFNO1FBQ04sT0FBTyxJQUFJRyxTQUFTLE1BQU07WUFBRUMsUUFBUTtRQUFJO0lBQzFDO0FBQ0YiLCJzb3VyY2VzIjpbIkQ6XFxEZXZcXHJlcG9zXFxwbGV4LW1jcFxcd2ViYXBwXFxmcm9udGVuZFxcYXBwXFxhcGlcXGxsbVxcbW9kZWxzXFxyb3V0ZS50cyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBOZXh0UmVxdWVzdCB9IGZyb20gXCJuZXh0L3NlcnZlclwiO1xyXG5pbXBvcnQgeyBwcm94eUdldCB9IGZyb20gXCJAL2xpYi9wcm94eVwiO1xyXG5cclxuZXhwb3J0IGFzeW5jIGZ1bmN0aW9uIEdFVChyZXF1ZXN0OiBOZXh0UmVxdWVzdCkge1xyXG4gIHRyeSB7XHJcbiAgICBjb25zdCB7IHNlYXJjaFBhcmFtcyB9ID0gbmV3IFVSTChyZXF1ZXN0LnVybCk7XHJcbiAgICByZXR1cm4gYXdhaXQgcHJveHlHZXQoXCIvYXBpL2xsbS9tb2RlbHNcIiwgc2VhcmNoUGFyYW1zKTtcclxuICB9IGNhdGNoIHtcclxuICAgIHJldHVybiBuZXcgUmVzcG9uc2UobnVsbCwgeyBzdGF0dXM6IDUwMiB9KTtcclxuICB9XHJcbn1cclxuIl0sIm5hbWVzIjpbInByb3h5R2V0IiwiR0VUIiwicmVxdWVzdCIsInNlYXJjaFBhcmFtcyIsIlVSTCIsInVybCIsIlJlc3BvbnNlIiwic3RhdHVzIl0sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./app/api/llm/models/route.ts\n");

/***/ }),

/***/ "(rsc)/./lib/proxy.ts":
/*!**********************!*\
  !*** ./lib/proxy.ts ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   proxyGet: () => (/* binding */ proxyGet)\n/* harmony export */ });\n/* harmony import */ var next_server__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/server */ \"(rsc)/./node_modules/next/dist/api/server.js\");\n\nconst BACKEND_URL = (process.env.API_URL || \"http://127.0.0.1:10740\" || 0).replace(\"localhost\", \"127.0.0.1\");\nconst PROXY_TIMEOUT_MS = 15000;\nasync function proxyGet(path, searchParams) {\n    const url = searchParams ? `${BACKEND_URL}${path}?${typeof searchParams === \"string\" ? searchParams : searchParams.toString()}` : `${BACKEND_URL}${path}`;\n    const controller = new AbortController();\n    const t = setTimeout(()=>controller.abort(), PROXY_TIMEOUT_MS);\n    try {\n        const res = await fetch(url, {\n            signal: controller.signal,\n            cache: \"no-store\"\n        });\n        if (!res.ok) {\n            let errBody = {\n                error: `Backend returned ${res.status}`\n            };\n            try {\n                const text = await res.text();\n                if (text) {\n                    try {\n                        errBody = JSON.parse(text);\n                    } catch  {\n                        errBody = {\n                            error: text.slice(0, 500)\n                        };\n                    }\n                }\n            } catch  {\n            /* ignore */ }\n            return next_server__WEBPACK_IMPORTED_MODULE_0__.NextResponse.json(errBody, {\n                status: res.status\n            });\n        }\n        return new next_server__WEBPACK_IMPORTED_MODULE_0__.NextResponse(res.body, {\n            status: res.status,\n            headers: {\n                \"Content-Type\": res.headers.get(\"content-type\") ?? \"application/json\"\n            }\n        });\n    } finally{\n        clearTimeout(t);\n    }\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9saWIvcHJveHkudHMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBMkM7QUFFM0MsTUFBTUMsY0FBYyxDQUNsQkMsUUFBUUMsR0FBRyxDQUFDQyxPQUFPLElBQ25CRix3QkFBK0IsSUFDL0IsQ0FBdUIsRUFDdkJJLE9BQU8sQ0FBQyxhQUFhO0FBQ3ZCLE1BQU1DLG1CQUFtQjtBQUVsQixlQUFlQyxTQUNwQkMsSUFBWSxFQUNaQyxZQUF1QztJQUV2QyxNQUFNQyxNQUFNRCxlQUNSLEdBQUdULGNBQWNRLEtBQUssQ0FBQyxFQUFFLE9BQU9DLGlCQUFpQixXQUFXQSxlQUFlQSxhQUFhRSxRQUFRLElBQUksR0FDcEcsR0FBR1gsY0FBY1EsTUFBTTtJQUMzQixNQUFNSSxhQUFhLElBQUlDO0lBQ3ZCLE1BQU1DLElBQUlDLFdBQVcsSUFBTUgsV0FBV0ksS0FBSyxJQUFJVjtJQUMvQyxJQUFJO1FBQ0YsTUFBTVcsTUFBTSxNQUFNQyxNQUFNUixLQUFLO1lBQzNCUyxRQUFRUCxXQUFXTyxNQUFNO1lBQ3pCQyxPQUFPO1FBQ1Q7UUFDQSxJQUFJLENBQUNILElBQUlJLEVBQUUsRUFBRTtZQUNYLElBQUlDLFVBQStDO2dCQUNqREMsT0FBTyxDQUFDLGlCQUFpQixFQUFFTixJQUFJTyxNQUFNLEVBQUU7WUFDekM7WUFDQSxJQUFJO2dCQUNGLE1BQU1DLE9BQU8sTUFBTVIsSUFBSVEsSUFBSTtnQkFDM0IsSUFBSUEsTUFBTTtvQkFDUixJQUFJO3dCQUNGSCxVQUFVSSxLQUFLQyxLQUFLLENBQUNGO29CQUN2QixFQUFFLE9BQU07d0JBQ05ILFVBQVU7NEJBQUVDLE9BQU9FLEtBQUtHLEtBQUssQ0FBQyxHQUFHO3dCQUFLO29CQUN4QztnQkFDRjtZQUNGLEVBQUUsT0FBTTtZQUNOLFVBQVUsR0FDWjtZQUNBLE9BQU83QixxREFBWUEsQ0FBQzhCLElBQUksQ0FBQ1AsU0FBUztnQkFBRUUsUUFBUVAsSUFBSU8sTUFBTTtZQUFDO1FBQ3pEO1FBQ0EsT0FBTyxJQUFJekIscURBQVlBLENBQUNrQixJQUFJYSxJQUFJLEVBQUU7WUFDaENOLFFBQVFQLElBQUlPLE1BQU07WUFDbEJPLFNBQVM7Z0JBQUUsZ0JBQWdCZCxJQUFJYyxPQUFPLENBQUNDLEdBQUcsQ0FBQyxtQkFBbUI7WUFBbUI7UUFDbkY7SUFDRixTQUFVO1FBQ1JDLGFBQWFuQjtJQUNmO0FBQ0YiLCJzb3VyY2VzIjpbIkQ6XFxEZXZcXHJlcG9zXFxwbGV4LW1jcFxcd2ViYXBwXFxmcm9udGVuZFxcbGliXFxwcm94eS50cyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBOZXh0UmVzcG9uc2UgfSBmcm9tIFwibmV4dC9zZXJ2ZXJcIjtcclxuXHJcbmNvbnN0IEJBQ0tFTkRfVVJMID0gKFxyXG4gIHByb2Nlc3MuZW52LkFQSV9VUkwgfHxcclxuICBwcm9jZXNzLmVudi5ORVhUX1BVQkxJQ19BUElfVVJMIHx8XHJcbiAgXCJodHRwOi8vMTI3LjAuMC4xOjEwNzQwXCJcclxuKS5yZXBsYWNlKFwibG9jYWxob3N0XCIsIFwiMTI3LjAuMC4xXCIpO1xyXG5jb25zdCBQUk9YWV9USU1FT1VUX01TID0gMTUwMDA7XHJcblxyXG5leHBvcnQgYXN5bmMgZnVuY3Rpb24gcHJveHlHZXQoXHJcbiAgcGF0aDogc3RyaW5nLFxyXG4gIHNlYXJjaFBhcmFtcz86IFVSTFNlYXJjaFBhcmFtcyB8IHN0cmluZ1xyXG4pOiBQcm9taXNlPE5leHRSZXNwb25zZT4ge1xyXG4gIGNvbnN0IHVybCA9IHNlYXJjaFBhcmFtc1xyXG4gICAgPyBgJHtCQUNLRU5EX1VSTH0ke3BhdGh9PyR7dHlwZW9mIHNlYXJjaFBhcmFtcyA9PT0gXCJzdHJpbmdcIiA/IHNlYXJjaFBhcmFtcyA6IHNlYXJjaFBhcmFtcy50b1N0cmluZygpfWBcclxuICAgIDogYCR7QkFDS0VORF9VUkx9JHtwYXRofWA7XHJcbiAgY29uc3QgY29udHJvbGxlciA9IG5ldyBBYm9ydENvbnRyb2xsZXIoKTtcclxuICBjb25zdCB0ID0gc2V0VGltZW91dCgoKSA9PiBjb250cm9sbGVyLmFib3J0KCksIFBST1hZX1RJTUVPVVRfTVMpO1xyXG4gIHRyeSB7XHJcbiAgICBjb25zdCByZXMgPSBhd2FpdCBmZXRjaCh1cmwsIHtcclxuICAgICAgc2lnbmFsOiBjb250cm9sbGVyLnNpZ25hbCxcclxuICAgICAgY2FjaGU6IFwibm8tc3RvcmVcIixcclxuICAgIH0pO1xyXG4gICAgaWYgKCFyZXMub2spIHtcclxuICAgICAgbGV0IGVyckJvZHk6IHsgZXJyb3I/OiBzdHJpbmc7IGRldGFpbD86IHN0cmluZyB9ID0ge1xyXG4gICAgICAgIGVycm9yOiBgQmFja2VuZCByZXR1cm5lZCAke3Jlcy5zdGF0dXN9YCxcclxuICAgICAgfTtcclxuICAgICAgdHJ5IHtcclxuICAgICAgICBjb25zdCB0ZXh0ID0gYXdhaXQgcmVzLnRleHQoKTtcclxuICAgICAgICBpZiAodGV4dCkge1xyXG4gICAgICAgICAgdHJ5IHtcclxuICAgICAgICAgICAgZXJyQm9keSA9IEpTT04ucGFyc2UodGV4dCk7XHJcbiAgICAgICAgICB9IGNhdGNoIHtcclxuICAgICAgICAgICAgZXJyQm9keSA9IHsgZXJyb3I6IHRleHQuc2xpY2UoMCwgNTAwKSB9O1xyXG4gICAgICAgICAgfVxyXG4gICAgICAgIH1cclxuICAgICAgfSBjYXRjaCB7XHJcbiAgICAgICAgLyogaWdub3JlICovXHJcbiAgICAgIH1cclxuICAgICAgcmV0dXJuIE5leHRSZXNwb25zZS5qc29uKGVyckJvZHksIHsgc3RhdHVzOiByZXMuc3RhdHVzIH0pO1xyXG4gICAgfVxyXG4gICAgcmV0dXJuIG5ldyBOZXh0UmVzcG9uc2UocmVzLmJvZHksIHtcclxuICAgICAgc3RhdHVzOiByZXMuc3RhdHVzLFxyXG4gICAgICBoZWFkZXJzOiB7IFwiQ29udGVudC1UeXBlXCI6IHJlcy5oZWFkZXJzLmdldChcImNvbnRlbnQtdHlwZVwiKSA/PyBcImFwcGxpY2F0aW9uL2pzb25cIiB9LFxyXG4gICAgfSk7XHJcbiAgfSBmaW5hbGx5IHtcclxuICAgIGNsZWFyVGltZW91dCh0KTtcclxuICB9XHJcbn1cclxuIl0sIm5hbWVzIjpbIk5leHRSZXNwb25zZSIsIkJBQ0tFTkRfVVJMIiwicHJvY2VzcyIsImVudiIsIkFQSV9VUkwiLCJORVhUX1BVQkxJQ19BUElfVVJMIiwicmVwbGFjZSIsIlBST1hZX1RJTUVPVVRfTVMiLCJwcm94eUdldCIsInBhdGgiLCJzZWFyY2hQYXJhbXMiLCJ1cmwiLCJ0b1N0cmluZyIsImNvbnRyb2xsZXIiLCJBYm9ydENvbnRyb2xsZXIiLCJ0Iiwic2V0VGltZW91dCIsImFib3J0IiwicmVzIiwiZmV0Y2giLCJzaWduYWwiLCJjYWNoZSIsIm9rIiwiZXJyQm9keSIsImVycm9yIiwic3RhdHVzIiwidGV4dCIsIkpTT04iLCJwYXJzZSIsInNsaWNlIiwianNvbiIsImJvZHkiLCJoZWFkZXJzIiwiZ2V0IiwiY2xlYXJUaW1lb3V0Il0sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./lib/proxy.ts\n");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fllm%2Fmodels%2Froute&page=%2Fapi%2Fllm%2Fmodels%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fllm%2Fmodels%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!":
/*!**********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fllm%2Fmodels%2Froute&page=%2Fapi%2Fllm%2Fmodels%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fllm%2Fmodels%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D! ***!
  \**********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   patchFetch: () => (/* binding */ patchFetch),\n/* harmony export */   routeModule: () => (/* binding */ routeModule),\n/* harmony export */   serverHooks: () => (/* binding */ serverHooks),\n/* harmony export */   workAsyncStorage: () => (/* binding */ workAsyncStorage),\n/* harmony export */   workUnitAsyncStorage: () => (/* binding */ workUnitAsyncStorage)\n/* harmony export */ });\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/dist/server/route-modules/app-route/module.compiled */ \"(rsc)/./node_modules/next/dist/server/route-modules/app-route/module.compiled.js\");\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! next/dist/server/route-kind */ \"(rsc)/./node_modules/next/dist/server/route-kind.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! next/dist/server/lib/patch-fetch */ \"(rsc)/./node_modules/next/dist/server/lib/patch-fetch.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var D_Dev_repos_plex_mcp_webapp_frontend_app_api_llm_models_route_ts__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app/api/llm/models/route.ts */ \"(rsc)/./app/api/llm/models/route.ts\");\n\n\n\n\n// We inject the nextConfigOutput here so that we can use them in the route\n// module.\nconst nextConfigOutput = \"standalone\"\nconst routeModule = new next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__.AppRouteRouteModule({\n    definition: {\n        kind: next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__.RouteKind.APP_ROUTE,\n        page: \"/api/llm/models/route\",\n        pathname: \"/api/llm/models\",\n        filename: \"route\",\n        bundlePath: \"app/api/llm/models/route\"\n    },\n    resolvedPagePath: \"D:\\\\Dev\\\\repos\\\\plex-mcp\\\\webapp\\\\frontend\\\\app\\\\api\\\\llm\\\\models\\\\route.ts\",\n    nextConfigOutput,\n    userland: D_Dev_repos_plex_mcp_webapp_frontend_app_api_llm_models_route_ts__WEBPACK_IMPORTED_MODULE_3__\n});\n// Pull out the exports that we need to expose from the module. This should\n// be eliminated when we've moved the other routes to the new format. These\n// are used to hook into the route.\nconst { workAsyncStorage, workUnitAsyncStorage, serverHooks } = routeModule;\nfunction patchFetch() {\n    return (0,next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__.patchFetch)({\n        workAsyncStorage,\n        workUnitAsyncStorage\n    });\n}\n\n\n//# sourceMappingURL=app-route.js.map//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9ub2RlX21vZHVsZXMvbmV4dC9kaXN0L2J1aWxkL3dlYnBhY2svbG9hZGVycy9uZXh0LWFwcC1sb2FkZXIvaW5kZXguanM/bmFtZT1hcHAlMkZhcGklMkZsbG0lMkZtb2RlbHMlMkZyb3V0ZSZwYWdlPSUyRmFwaSUyRmxsbSUyRm1vZGVscyUyRnJvdXRlJmFwcFBhdGhzPSZwYWdlUGF0aD1wcml2YXRlLW5leHQtYXBwLWRpciUyRmFwaSUyRmxsbSUyRm1vZGVscyUyRnJvdXRlLnRzJmFwcERpcj1EJTNBJTVDRGV2JTVDcmVwb3MlNUNwbGV4LW1jcCU1Q3dlYmFwcCU1Q2Zyb250ZW5kJTVDYXBwJnBhZ2VFeHRlbnNpb25zPXRzeCZwYWdlRXh0ZW5zaW9ucz10cyZwYWdlRXh0ZW5zaW9ucz1qc3gmcGFnZUV4dGVuc2lvbnM9anMmcm9vdERpcj1EJTNBJTVDRGV2JTVDcmVwb3MlNUNwbGV4LW1jcCU1Q3dlYmFwcCU1Q2Zyb250ZW5kJmlzRGV2PXRydWUmdHNjb25maWdQYXRoPXRzY29uZmlnLmpzb24mYmFzZVBhdGg9JmFzc2V0UHJlZml4PSZuZXh0Q29uZmlnT3V0cHV0PXN0YW5kYWxvbmUmcHJlZmVycmVkUmVnaW9uPSZtaWRkbGV3YXJlQ29uZmlnPWUzMCUzRCEiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7Ozs7QUFBK0Y7QUFDdkM7QUFDcUI7QUFDMkI7QUFDeEc7QUFDQTtBQUNBO0FBQ0Esd0JBQXdCLHlHQUFtQjtBQUMzQztBQUNBLGNBQWMsa0VBQVM7QUFDdkI7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBLFlBQVk7QUFDWixDQUFDO0FBQ0Q7QUFDQTtBQUNBO0FBQ0EsUUFBUSxzREFBc0Q7QUFDOUQ7QUFDQSxXQUFXLDRFQUFXO0FBQ3RCO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDMEY7O0FBRTFGIiwic291cmNlcyI6WyIiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgQXBwUm91dGVSb3V0ZU1vZHVsZSB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL3JvdXRlLW1vZHVsZXMvYXBwLXJvdXRlL21vZHVsZS5jb21waWxlZFwiO1xuaW1wb3J0IHsgUm91dGVLaW5kIH0gZnJvbSBcIm5leHQvZGlzdC9zZXJ2ZXIvcm91dGUta2luZFwiO1xuaW1wb3J0IHsgcGF0Y2hGZXRjaCBhcyBfcGF0Y2hGZXRjaCB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL2xpYi9wYXRjaC1mZXRjaFwiO1xuaW1wb3J0ICogYXMgdXNlcmxhbmQgZnJvbSBcIkQ6XFxcXERldlxcXFxyZXBvc1xcXFxwbGV4LW1jcFxcXFx3ZWJhcHBcXFxcZnJvbnRlbmRcXFxcYXBwXFxcXGFwaVxcXFxsbG1cXFxcbW9kZWxzXFxcXHJvdXRlLnRzXCI7XG4vLyBXZSBpbmplY3QgdGhlIG5leHRDb25maWdPdXRwdXQgaGVyZSBzbyB0aGF0IHdlIGNhbiB1c2UgdGhlbSBpbiB0aGUgcm91dGVcbi8vIG1vZHVsZS5cbmNvbnN0IG5leHRDb25maWdPdXRwdXQgPSBcInN0YW5kYWxvbmVcIlxuY29uc3Qgcm91dGVNb2R1bGUgPSBuZXcgQXBwUm91dGVSb3V0ZU1vZHVsZSh7XG4gICAgZGVmaW5pdGlvbjoge1xuICAgICAgICBraW5kOiBSb3V0ZUtpbmQuQVBQX1JPVVRFLFxuICAgICAgICBwYWdlOiBcIi9hcGkvbGxtL21vZGVscy9yb3V0ZVwiLFxuICAgICAgICBwYXRobmFtZTogXCIvYXBpL2xsbS9tb2RlbHNcIixcbiAgICAgICAgZmlsZW5hbWU6IFwicm91dGVcIixcbiAgICAgICAgYnVuZGxlUGF0aDogXCJhcHAvYXBpL2xsbS9tb2RlbHMvcm91dGVcIlxuICAgIH0sXG4gICAgcmVzb2x2ZWRQYWdlUGF0aDogXCJEOlxcXFxEZXZcXFxccmVwb3NcXFxccGxleC1tY3BcXFxcd2ViYXBwXFxcXGZyb250ZW5kXFxcXGFwcFxcXFxhcGlcXFxcbGxtXFxcXG1vZGVsc1xcXFxyb3V0ZS50c1wiLFxuICAgIG5leHRDb25maWdPdXRwdXQsXG4gICAgdXNlcmxhbmRcbn0pO1xuLy8gUHVsbCBvdXQgdGhlIGV4cG9ydHMgdGhhdCB3ZSBuZWVkIHRvIGV4cG9zZSBmcm9tIHRoZSBtb2R1bGUuIFRoaXMgc2hvdWxkXG4vLyBiZSBlbGltaW5hdGVkIHdoZW4gd2UndmUgbW92ZWQgdGhlIG90aGVyIHJvdXRlcyB0byB0aGUgbmV3IGZvcm1hdC4gVGhlc2Vcbi8vIGFyZSB1c2VkIHRvIGhvb2sgaW50byB0aGUgcm91dGUuXG5jb25zdCB7IHdvcmtBc3luY1N0b3JhZ2UsIHdvcmtVbml0QXN5bmNTdG9yYWdlLCBzZXJ2ZXJIb29rcyB9ID0gcm91dGVNb2R1bGU7XG5mdW5jdGlvbiBwYXRjaEZldGNoKCkge1xuICAgIHJldHVybiBfcGF0Y2hGZXRjaCh7XG4gICAgICAgIHdvcmtBc3luY1N0b3JhZ2UsXG4gICAgICAgIHdvcmtVbml0QXN5bmNTdG9yYWdlXG4gICAgfSk7XG59XG5leHBvcnQgeyByb3V0ZU1vZHVsZSwgd29ya0FzeW5jU3RvcmFnZSwgd29ya1VuaXRBc3luY1N0b3JhZ2UsIHNlcnZlckhvb2tzLCBwYXRjaEZldGNoLCAgfTtcblxuLy8jIHNvdXJjZU1hcHBpbmdVUkw9YXBwLXJvdXRlLmpzLm1hcCJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fllm%2Fmodels%2Froute&page=%2Fapi%2Fllm%2Fmodels%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fllm%2Fmodels%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!\n");

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
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/next"], () => (__webpack_exec__("(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Fllm%2Fmodels%2Froute&page=%2Fapi%2Fllm%2Fmodels%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fllm%2Fmodels%2Froute.ts&appDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=D%3A%5CDev%5Crepos%5Cplex-mcp%5Cwebapp%5Cfrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!")));
module.exports = __webpack_exports__;

})();