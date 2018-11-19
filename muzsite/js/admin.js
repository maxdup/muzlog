require('jquery/dist/jquery.js')
require('angular/angular.js');
require('angular-animate/angular-animate.js');
require('@uirouter/angularjs');

require('./admin_controller.js');
require('./resources.js');

module.exports = angular.module('muzApp', [
  'ui.router', 'ngAnimate', 'muz.adminCtrl', 'muz.resources'])
  .config([
    "$locationProvider", "$stateProvider", "$urlRouterProvider",
    function($locationProvider, $stateProvider, $urlRouterProvider,){
      $stateProvider
        .state('admin', {
          url: '/admin',
          templateUrl: '/static/partials/admin/home.html',
          controller: 'AdminController'
        })
        .state('admin.edit_album', {
          url: '/edit/:id',
          templateUrl: '/static/partials/admin/edit.html',
          controller: 'EditAlbumController'
        })
      $urlRouterProvider.otherwise('/admin', {
        url: '/',
        templateUrl: '/static/partials/admin/home.html',
        controller: 'AdminController'
      });
      $locationProvider.html5Mode(true);
    }])


