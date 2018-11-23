window.$ = require("expose-loader?$!jquery");
require('@uirouter/angularjs');
require('angular-animate/angular-animate.js');

require('./album_controller.js');
require('./user_controller.js');
require('./log_controller.js');
require('./resources.js');
require('./directives.js');

module.exports = angular.module('muzApp', [
  'ui.materialize', 'ui.router', 'ngAnimate', 'muz.resources',
  'muz.albumCtrl', 'muz.userCtrl', 'muz.logCtrl', 'muz.adminDirectives'])
  .config([
    "$locationProvider", "$stateProvider", "$urlRouterProvider",
    function($locationProvider, $stateProvider, $urlRouterProvider){
      $stateProvider
        .state('view_albums', {
          url: '/cms',
          templateUrl: '/static/partials/admin/view_albums.html',
          controller: 'ViewAlbumsController'
        })
        .state('create_album', {
          url: '/cms/album/create',
          templateUrl: '/static/partials/admin/create_album.html',
          controller: 'CreateAlbumController'
        })
        .state('edit_album', {
          url: '/cms/album/edit/:aid',
          templateUrl: '/static/partials/admin/edit_album.html',
          controller: 'EditAlbumController'
        })
        .state('create_log', {
          url: '/cms/log/create/:aid',
          templateUrl: '/static/partials/admin/create_log.html',
          controller: 'CreateLogController'
        })
        .state('view_logs', {
          url: '/cms/log/:uid',
          templateUrl: '/static/partials/admin/view_logs.html',
          controller: 'ViewLogsController'
        })
        .state('view_profiles', {
          url: '/cms/profiles',
          templateUrl: '/static/partials/admin/view_profiles.html',
          controller: 'ViewProfilesController'
        })
        .state('edit_profile', {
          url: '/cms/profile/:uid',
          templateUrl: '/static/partials/admin/edit_profile.html',
          controller: 'EditProfileController'
        })
        .state('edit_roles', {
          url: '/cms/roles',
          templateUrl: '/static/partials/admin/edit_roles.html',
          controller: 'EditRolesController'
        })

      $urlRouterProvider.otherwise('/cms', {
        url: '/',
        templateUrl: '/static/partials/admin/home.html',
        controller: 'AdminController'
      });
      $locationProvider.html5Mode(true);
    }])
  .constant('conf', { img_url: 'http://127.0.0.1/muzlogcovers/'})
  .controller('RootController', [
    "$rootScope", "Profile", "conf", function($rootScope, Profile, conf){
      $rootScope.conf = conf;
      Profile.me().$promise.then(function(value){
        $rootScope.profile = value.profile;
      });
    }]);
