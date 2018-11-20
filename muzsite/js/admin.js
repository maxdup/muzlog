window.$ = require("expose-loader?$!jquery");
require('@uirouter/angularjs');
require('angular-animate/angular-animate.js');

angular.module('yourModule', []);

require('./admin_controller.js');
require('./resources.js');

module.exports = angular.module('muzApp', [
  'ui.materialize', 'ui.router', 'ngAnimate',
  'muz.adminCtrl', 'muz.resources'])
  .config([
    "$locationProvider", "$stateProvider", "$urlRouterProvider",
    function($locationProvider, $stateProvider, $urlRouterProvider,){
      $stateProvider
        .state('admin', {
          url: '/admin',
          templateUrl: '/static/partials/admin/home.html',
          controller: 'AdminController'
        })
        .state('create_album', {
          url: '/admin/create',
          templateUrl: '/static/partials/admin/create_album.html',
          controller: 'CreateAlbumController'
        })
        .state('edit_album', {
          url: '/admin/edit/:id',
          templateUrl: '/static/partials/admin/edit_album.html',
          controller: 'EditAlbumController'
        })
      $urlRouterProvider.otherwise('/admin', {
        url: '/',
        templateUrl: '/static/partials/admin/home.html',
        controller: 'AdminController'
      });
      $locationProvider.html5Mode(true);
    }])


