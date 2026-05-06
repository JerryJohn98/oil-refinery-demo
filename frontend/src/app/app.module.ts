import { NgModule, Injector } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppComponent } from './app.component';
import { NgSelectModule } from '@ng-select/ng-select';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { createCustomElement } from '@angular/elements';
import { DatePipe } from '@angular/common';


@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    NgSelectModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
  ],
  exports: [OwlDateTimeModule, OwlNativeDateTimeModule],
  providers: [DatePipe]
})
export class AppModule {
  constructor(public injector: Injector) {
    if (!customElements.get('oil-refinery')) {
      customElements.define('oil-refinery', createCustomElement(AppComponent, { injector: this.injector }));
    }
  }

    ngDoBootstrap() {}
}
