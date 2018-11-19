require('jquery/dist/jquery.js')
require('angular/angular.js');
require('angular-resource/angular-resource.js');
require('@uirouter/angularjs');

module.exports = angular.module('szApp', ['ui.router', 'ngAnimate'])
  .config([
    "$locationProvider", "$stateProvider", "$urlRouterProvider",
    function($locationProvider, $stateProvider, $urlRouterProvider,){

      $stateProvider
        .state('home', {
          url: '/',
          tempalteUrl: 'home.html',
        })
      $locationProvider.html5Mode(true);
    }]);

