_ = require('lodash');
require('ng-file-upload');
module.exports = angular.module('muz.adminDirectives', ['ngFileUpload'])

  .directive('logCreator', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        albumId: "@",
        onCreate: '='
      },
     templateUrl: '/static/partials/directives/log_create.html',
      controller: ["$scope", "Log", function($scope, Log) {
        $scope.log = {};

        $scope.publish_log = function(log){
          log.published = true;
          $scope.save_log(log);
        }
        $scope.save_log = function(log){
          log.album_id = $scope.albumId;
          Log.save(log).$promise.then(function(value){
            $scope.onCreate(value);
            $scope.log = {};
          });
        }
      }]
    }
  })
  .directive('logDisplay', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        log: '=ngModel',
        onDelete: '&',
      },
      templateUrl: '/static/partials/directives/log_display.html',
      controller: ["$scope", "Log", function($scope, Log) {

        $scope.enable_edit = true;
        $scope.open_edit = function(){
          $scope.backup = _.cloneDeep($scope.log);
        }
        $scope.cancel_edit = function(){
          $scope.log = $scope.backup;
          $scope.backup = null;
        }
        $scope.save_changes = function(){
          Log.update($scope.log)
            .$promise.then(function(value){
              $scope.log = value.log;
              $scope.backup = null;
            })
        }
        $scope.publish = function(){
          Log.update({id: $scope.log.id, published: true})
            .$promise.then(function(value){
              $scope.log = _.extend($scope.log, value.log);
            }, function(err){
              $scope.log.published = false;
            })
        }
        $scope.delete_log = function(){
          if (confirm("This log will be deleted")){
            Log.delete({id:$scope.log.id})
              .$promise.then($scope.onDelete);
          }
        }
      }]
    }
  })

  .directive('albumSummary', function() {
    return {
      restrict: 'EA',
      replace: true,
      scope: { album: "=ngModel" },
      link : function(scope, element, attrs){
        scope.enable_edit = attrs.editable != undefined;
      },
      templateUrl: '/static/partials/directives/album_summary.html',
      controller: ["$scope", "conf", function($scope, conf) {
        $scope.conf = conf;
      }]
    }
  })

  .directive('albumDisplay', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: { album: '=ngModel', },
      templateUrl: '/static/partials/directives/album_display.html',
    }
  })
  .directive('profileDisplay', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        profile: '=ngModel',
      },
      templateUrl: '/static/partials/directives/profile_display.html',
      controller: [
        "$scope", "Profile", "conf", 'UploadService',
        function($scope, Profile, conf, UploadService) {
          $scope.conf = conf;
          $scope.enable_edit = true;
          $scope.open_edit = function(){
            $scope.backup = _.cloneDeep($scope.profile);
          }
          $scope.select_file = function(files){
            if (files.length > 0){
              $scope.avatar_file = files[0];
            }
          }
          $scope.save_changes = function(){
            Profile.update($scope.profile)
              .$promise.then(function(value){
                $scope.profile = value.profile;
                if ($scope.avatar_file){
                  var url = '/api/upload_profile_avatar/'+ $scope.profile.id;
                  UploadService.upload(url, $scope.avatar_file)
                    .then(function(result){
                      $scope.profile.thumb = result.data;
                      $scope.avatar_file = null;
                      $scope.backup = null;
                    }, function(err){
                      alert('there was a problem saving the avatar',);
                      $scope.backup = null;
                    })
                } else {
                  $scope.backup = null;
                }
              })
          }
          $scope.cancel_changes = function(){
            $scope.profile = $scope.backup;
            $scope.backup = null;
          }
        }]
    }
  })
  .directive('avatarDisplay', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: { profile: '=ngModel', },
      templateUrl: '/static/partials/directives/profile_avatar.html',
    }
  })

  .directive('albumCreator', function() {
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        album: "=ngModel",
        onCreate: '=',
      },
      templateUrl: '/static/partials/directives/album_create.html',
      controller: [
        "$state", "$scope", "$http", "Album", "Upload", "conf", "$q",
        function($state, $scope, $http, Album, Upload, conf, $q) {
          $scope.conf = conf;
          $scope.album = {};

          $scope.search = function(search_term){
            $http.get('http://musicbrainz.org/ws/2/release/?query=' +
                      search_term + '&fmt=json')
              .then(function(value){
                $scope.search_results = value.data.releases;
              });
          }

          $scope.select_search_result = function(result){
            $scope.mb_album = result;
            $scope.mb_album.mbid = $scope.mb_album.id;
          }

          $scope.unselect_search_result = function(){
            $scope.mb_album = null;
          }

          function album_saved(value){
            if ($scope.onCreate){
              $scope.album = value;
              $scope.onCreate(value);
            }
          }
          $scope.save_album = function(){
            Album.save($scope.album).$promise.then(function(value){
              upload($scope.cover_file, value.album.id).then(
                function(result){
                  album_saved(value);
                }, function(err){
                  album_saved(value);
                });
            });
          }
          $scope.save_brainz_album = function(){
            Album.save($scope.mb_album).$promise.then(album_saved);
          }

          $scope.select_file = function(files){
            if (files.length > 0){
              $scope.cover_file = files[0];
            }
          }
          var upload = function(cover_file, album_id){
            return $q(function(resolve, reject) {
              Upload.upload({
	            url: '/upload_album_cover/' + album_id,
                data: { file: cover_file }})
                .then(resolve,reject);
            });
          }
        }]
    }
  });
