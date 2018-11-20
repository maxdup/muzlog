module.exports = angular.module('muz.adminCtrl', [])


  .controller('AdminController', [
    '$scope', 'Album', function($scope, Album) {
      Album.get().$promise.then(function(value){
        $scope.albums = value.albums;
        console.log($scope.albums);
      });
    }])


  .controller('EditAlbumController', [
    '$stateParams', '$scope', 'Album', '$http',
    function($stateParams, $scope, Album, $http) {

      Album.get({id:$stateParams.id}).$promise.then(function(value){
        $scope.album = value;
        console.log('album', $scope.album);
      });

    }])
  .controller('CreateAlbumController', [
    '$scope', function($scope){
      $scope.album = {};
      $scope.album_created = function(val){
        console.log('callback!', $scope.album);
      }
    }])

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
          $scope.save_manual_album = function(){
            Album.save($scope.album).$promise.then(album_saved);
          }
          $scope.save_brainz_album = function(){
            $scope.mb_album.mbid = $scope.mb_album.id;
            Album.save($scope.mb_album).$promise.then(album_saved);
          }
        }]
    }
  })
