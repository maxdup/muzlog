module.exports = angular.module('muz.adminDirectives', [])
  .directive('albumSummary', function() {
    return {
      restrict: 'EA',
      replace: true,
      scope: {
	    ngModel: "=",
      },
      link : function(scope, element, attrs){
        scope.enable_edit = attrs.editable != undefined;
      },
      templateUrl: '/static/partials/admin/directives/summarize_album.html',
    }
  })
  .directive('logCreator', function(){
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        albumId: "@",
        onCreate: '='
      },
      templateUrl: '/static/partials/admin/directives/log_album.html',
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
        }],
    }
  })
  .directive('albumCreator', function() {
    return {
      restrict: 'EA',
      replace: true,
      scope: {
        ngModel: "=",
        onCreate: '&',
      },
      templateUrl: '/static/partials/admin/directives/create_album.html',
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
              $scope.ngModel = value;
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
