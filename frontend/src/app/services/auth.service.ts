import { Injectable } from '@angular/core';
import * as CryptoJS from 'crypto-js';


@Injectable({
    providedIn: 'root',
  })

  export class AuthService {
    public waste = {
        k: '',
        li: '',
        Lens: '',
        KLiL: '',
        e: '',
        nsK: '',
        L: '',
      };
    getProjectDetails() {
        try {
          if (this.getSessionKey()) {
            const encryptedProjectDetails = localStorage.getItem('projectDetails');
            let decryptedProjectDetails = this.decryptId(encryptedProjectDetails);
            decryptedProjectDetails =
              decryptedProjectDetails && decryptedProjectDetails !== ''
                ? JSON.parse(decryptedProjectDetails)
                : null;
            decryptedProjectDetails =
              typeof decryptedProjectDetails === 'string'
                ? JSON.parse(decryptedProjectDetails)
                : decryptedProjectDetails;
            return decryptedProjectDetails;
          } else {
            return null;
          }
        } catch (error) {
          console.error(error);
          return null;
        }
      }
      getSessionKey() {
        const session_id = this.returnK();
        const parsed_session_id = CryptoJS.enc.Utf8.parse(session_id);
        return parsed_session_id;
      }
      returnK() {
        let k = '';
        for (const prop in this.waste) {
          k += prop;
        }
        return k;
      }
      decryptId(ciphertextStr: any) {
        const key = this.getSessionKey();
        const ciphertext = CryptoJS.enc.Base64.parse(ciphertextStr);
        const iv = ciphertext.clone();
        iv.sigBytes = 16;
        iv.clamp();
        const encryptedData = ciphertext.clone();
        encryptedData.words.splice(0, 4);
        encryptedData.sigBytes -= 16;
        const params = {
          ciphertext: encryptedData,
          iv: iv,
          key: key,
          salt: CryptoJS.lib.WordArray.create([]),
          algorithm: CryptoJS.algo.AES,
          mode: {
            processBlock: function () {},
          },
          padding: CryptoJS.pad.Pkcs7,
          blockSize: 128,
          formatter: CryptoJS.format.OpenSSL,
        };

        const decrypted = CryptoJS.AES.decrypt(params, key, {
          iv: iv,
        });

        const decryptedString = decrypted.toString(CryptoJS.enc.Utf8);
        return decryptedString;
      }

      getUserDetails() {
        try {
          if ( this.getSessionKey()) {
            if (localStorage.getItem('userDetails')) {
              const encryptedUserDetails = localStorage.getItem('userDetails');
              const decryptedUserDetails =  this.decryptId(encryptedUserDetails);
              return decryptedUserDetails && decryptedUserDetails !== '' ? JSON.parse(decryptedUserDetails) : null;
            }
          }
          return null;
        } catch (error) {
          console.error(error);
        }
      }
  }
