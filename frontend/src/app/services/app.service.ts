import { HttpLayerService } from './http-layer.service';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { Injectable } from '@angular/core';


@Injectable({
  providedIn: 'root',
})
export class AppService {
  public showSideBar = true;
  public notificationValue = new Subject<any>();
  public activeTab = new BehaviorSubject<any>('');
  public enableButton = new BehaviorSubject<any>('');
  public userDetails = new Subject<any>();

  public queryParams$ = this.activatedRoute.queryParamMap;

  constructor(
    private _httplayer: HttpLayerService,
    public activatedRoute: ActivatedRoute
  ) {}

  getHeaderDetails(): Observable<any> {
    return this._httplayer.getRequest('./assets/jsons/header.json');
  }
  getBodyContent(payload: any): Observable<any> {
    return this._httplayer.getRequest('./assets/jsons/bodyContent.json');
  }
}
