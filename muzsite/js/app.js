require('jquery/dist/jquery.js')
require('angular/angular.js');
require('angular-animate/angular-animate.js');
require('angular-resource/angular-resource.js');
require('@uirouter/angularjs');


module.exports = angular.module('muzApp', [
  'ui.router', 'ngAnimate', 'muz.adminCtrl'])
  .config([
    "$locationProvider", "$stateProvider", "$urlRouterProvider",
    function($locationProvider, $stateProvider, $urlRouterProvider,){

      $stateProvider
        .state('home', {
          url: '/',
          templateUrl: 'home.html',
        })
      $locationProvider.html5Mode(true);
    }])
  .constant('conf', { cover_url: 'http://127.0.0.1/muzlogcovers/'})
