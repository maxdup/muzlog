_ = require('lodash');
module.exports = angular.module('muz.adminDirectives', [])

  .directive('logCreator', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        albumId: "@",
        onCreate: '='
      },
     templateUrl: '/static/partials/admin/directives/log_create.html',
      controller: [
        "$scope", "Log", function($scope, Log) {

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
      templateUrl: '/static/partials/admin/directives/log_display.html',
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
      templateUrl: '/static/partials/admin/directives/album_summary.html',
    }
  })

  .directive('albumDisplay', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: { album: '=ngModel', },
      templateUrl: '/static/partials/admin/directives/album_display.html',
    }
  })

  .directive('albumCreator', function() {
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        album: "=ngModel",
        onCreate: '&',
      },
      templateUrl: '/static/partials/admin/directives/album_create.html',
      controller: [
        "$scope", "$http", "Album",
        function($scope, $http, Album) {
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
            Album.save($scope.album).$promise.then(album_saved);
          }
          $scope.save_brainz_album = function(){
            Album.save($scope.mb_album).$promise.then(album_saved);
          }
        }]
    }
  });
