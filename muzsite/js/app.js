angular.module('muzApp', [
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
  .constant('conf', { img_url: 'http://127.0.0.1/muzlogcovers/'})
