import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpRequest } from '@angular/common/http';
import { catchError, tap } from 'rxjs/operators';
import { throwError } from 'rxjs';
import * as CryptoJS from 'crypto-js';
import { AuthService } from './auth.service';
@Injectable({
    providedIn: 'root'
})

export class HttpLayerService {
    constructor(
        private http: HttpClient, public _auth:AuthService
    ) { }

    httpHeaders: any = new HttpHeaders({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,DELETE,PUT',
        'Access-Control-Allow-Headers': "Content-Type, x-requested-with"
    });

    public responseData: any;
    public waste = {
        k: '',
        li: '',
        Lens: '',
        KLiL: '',
        e: '',
        nsK: '',
        L: '',
    };
    detectContentType(method: any, url: any, data:any ) {
        const req = new HttpRequest(method, url, data);
        return req.detectContentTypeHeader();
    }
    base64url(source: any): string {
        let encodedSource = CryptoJS.enc.Base64.stringify(source);
        encodedSource = encodedSource.replace(/=+$/, '');
        encodedSource = encodedSource.replace(/\+/g, '-');
        encodedSource = encodedSource.replace(/\//g, '_');
        return encodedSource;
    }
    getSignedToken(payload: any): string | undefined {
        try {
            let vSign = false;
            if (localStorage.getItem('vSign')) {
                vSign = JSON.parse(this._auth.decryptId(localStorage.getItem('vSign')));
            }
            if (!vSign) {
                return payload;
            }
            const secretKey = Object.keys(this.waste).join('');
            const header = {
                alg: 'HS256',
                typ: 'JWT',
            };
            const stringifiedHeader = CryptoJS.enc.Utf8.parse(JSON.stringify(header));
            const encodedHeader = this.base64url(stringifiedHeader);
            const stringifiedData = CryptoJS.enc.Utf8.parse(JSON.stringify(payload));
            const encodedData = this.base64url(stringifiedData);
            const token = encodedHeader + '.' + encodedData;
            let signature: any = CryptoJS.HmacSHA256(token, secretKey);
            signature = this.base64url(signature);
            return token + '.' + signature;
        } catch (e) {
          console.error(e);
          return undefined;
        }
    }


    postRequest(url: any, data: any) {
        return this.http.post(url, data, { headers: this.httpHeaders });
    }
    getRequest(url: any) {
        return this.http.get(url, { headers: this.httpHeaders });
    }

    post(url: any, data: any) {
        return this.http.post(url, this.getSignedToken(data), { headers: this.httpHeaders })
        .pipe(
            tap((res: any) => {
                this.responseData = res;
            }), catchError(error => {
                return throwError('Something went wrong!');
            })
        )
    }
}
