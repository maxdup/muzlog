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

      Album.get({id:$stateParams.id})
        .$promise.then(function(value){
          $scope.album = value;
          console.log('album', $scope.album);
        });

    }])

  .controller('CreateAlbumController', [
    '$scope', '$state', function($scope, $state){
      $scope.album = {};
      $scope.album_created = function(val){
        $state.go('log_album', {'id': $scope.album.id})
      }
    }])

  .controller('LogAlbumController', [
    '$stateParams', '$scope', 'Album', '$http',
    function($stateParams, $scope, Album, $http) {
      $scope.album = {};
      $scope.log_created = function(value){
        $scope.album.logs.push(value.log)
      }
      Album.get({'id': $stateParams.id})
        .$promise.then(function(value){
          $scope.album = value.album;
        });

    }])
