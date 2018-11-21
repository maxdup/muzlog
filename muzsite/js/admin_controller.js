module.exports = angular.module('muz.adminCtrl', [])

  .controller('AdminController', [
    '$scope', 'Album', function($scope, Album) {
      Album.get().$promise.then(function(value){
        $scope.albums = value.albums;
        console.log('albums', $scope.albums);
      });
    }])

  .controller('EditAlbumController', [
    '$stateParams', '$scope', 'Album', '$state',
    function($stateParams, $scope, Album, $state) {

      Album.get({id:$stateParams.id})
        .$promise.then(function(value){
          $scope.album = value.album;
        });

      $scope.save_changes = function(){
        Album.update($scope.album)
          .$promise.then(function(value){
            $scope.album = value.album;
            $state.go('create_log', {'id': value.album.id});
          })
      }

      $scope.delete_album = function(){
        if (confirm("This album will be deleted")){
          Album.delete({id:$scope.album.id})
            .$promise.then(function(){
              $state.go('admin');
            });
        }
      }
    }])

  .controller('CreateAlbumController', [
    '$scope', '$state', function($scope, $state){
      $scope.album = {};
      $scope.album_created = function(val){
        $state.go('create_log', {'id': val.album.id})
      }
    }])

  .controller('LogAlbumController', [
    '$stateParams', '$scope', 'Album', '$http',
    function($stateParams, $scope, Album, $http) {
      $scope.album = {};

      Album.get({'id': $stateParams.id})
        .$promise.then(function(value){
          $scope.album = value.album;
        });

      $scope.log_created = function(value){
        $scope.album.logs.push(value.log)
      }

      $scope.log_deleted = function(value){
        _.remove($scope.album.logs, {id: value.id});
      }

    }])
