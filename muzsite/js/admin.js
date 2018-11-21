window.$ = require("expose-loader?$!jquery");
require('@uirouter/angularjs');
require('angular-animate/angular-animate.js');

angular.module('yourModule', []);

require('./admin_controller.js');
require('./resources.js');
require('./directives.js');

module.exports = angular.module('muzApp', [
  'ui.materialize', 'ui.router', 'ngAnimate',
  'muz.adminCtrl', 'muz.resources', 'muz.adminDirectives'])
  .config([
    "$locationProvider", "$stateProvider", "$urlRouterProvider",
    function($locationProvider, $stateProvider, $urlRouterProvider,){
      $stateProvider
        .state('admin', {
          url: '/admin',
          templateUrl: '/static/partials/admin/home.html',
          controller: 'AdminController'
        })
        .state('edit_album', {
          url: '/admin/album/edit/:id',
          templateUrl: '/static/partials/admin/edit_album.html',
          controller: 'EditAlbumController'
        })
        .state('create_album', {
          url: '/admin/album/create',
          templateUrl: '/static/partials/admin/create_album.html',
          controller: 'CreateAlbumController'
        })
        .state('create_log', {
          url: '/admin/log/:id',
          templateUrl: '/static/partials/admin/create_log.html',
          controller: 'LogAlbumController'
        })

      $urlRouterProvider.otherwise('/admin', {
        url: '/',
        templateUrl: '/static/partials/admin/home.html',
        controller: 'AdminController'
      });
      $locationProvider.html5Mode(true);
    }])
  .constant('conf', { cover_url: 'http://127.0.0.1/muzlogcovers/'})

