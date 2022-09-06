// import { config } from './config'
const config = { baseUrl: "" }


export interface Dictionary<TValue> {
    [id: string]: TValue;
}

export interface APIResponseInternal {
    error: Error;
    data: any;
}

/**
 * fetch with url and headers 
 * 
 * @param url 
 * @param params optional
 * @returns Promise< <T> | Error>
 */
// TODO: y is error not shown as return type when its thrown in the catch?
// TODO, ASK: Dictionary<string> is needed for URLSearchParams but then i cant check for numbers in the calling functions
export function fetchEzy<T>(url: string, params?: Dictionary<any>) {
    // add base URL for internal API
    // internal API EPs have to start with _underscore
    var sUrl = url[0] === "_" || url[0] === "/_" ? config.baseUrl + url : url;
    console.log(sUrl)

    // Add params
    var bParamsAlready = sUrl.indexOf("?") !== -1 ? true : false;

    if (params) sUrl = bParamsAlready ?
        sUrl + "&" + new URLSearchParams(params) :
        sUrl + "?" + new URLSearchParams(params);

    console.log("[fetchEzy] " + sUrl)
    // console.log(sUrlWithParams)

    return fetch(sUrl)
        .then(res => {
            if (!res.ok) throw new Error(res.status.toString());

            const contentType = res.headers.get('content-type');
            // console.log(contentType)
            if (contentType && contentType.includes('application/json')) {
                return res.json() as Promise<{ error?: string }>
            }
            console.log("test in fetchEzy - her the respnse is not jsonified but turned to unknown n then promise with type")
            return res as unknown as Promise<T>;
        })
        .then(res => {
            // check internal api error response
            if (res.error?.length) throw new Error(JSON.stringify(res.error))
            return res as T;
        })
        .catch(err => {
            // return Promise.reject("could not fetch " + sUrl + ": " + err);
            throw new Error("could not fetch " + sUrl + ": " + err.stack);
        });
}
