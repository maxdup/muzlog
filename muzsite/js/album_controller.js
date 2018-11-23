module.exports = angular.module('muz.albumCtrl', [])

  .controller('ViewAlbumsController', [
    '$scope', 'Album', function($scope, Album) {
      Album.get().$promise.then(function(value){
        $scope.albums = value.albums;
      });
    }])

  .controller('EditAlbumController', [
    '$state', '$stateParams', '$scope', 'Album', 'UploadService', '$q', 'conf',
    function($state, $stateParams, $scope, Album, UploadService, $q, conf) {
      $scope.conf = conf;

      Album.get({id:$stateParams.aid})
        .$promise.then(function(value){
          $scope.album = value.album;
        });

      $scope.save_changes = function(){
        Album.update($scope.album)
          .$promise.then(function(value){
            if ($scope.cover_file){
              var url = '/api/upload_album_cover/' + value.album.id;
              UploadService.upload(url, $scope.cover_file)
                .then(function(result){
                  $scope.album = result.album;
                  $state.go('create_log', {'aid': value.album.id});
                }, function(){
                  $state.go('create_log', {'aid': value.album.id});
                });
              $scope.album = value.album;
            } else {
              $scope.album = value.album;
              $state.go('create_log', {'aid': value.album.id});
            }
          })
      }
      $scope.cancel_changes = function(){
        $state.go('create_log', {'aid': $scope.album.id});
      }

      $scope.delete_album = function(){
        if (confirm("This album will be deleted")){
          Album.delete({id:$scope.album.id})
            .$promise.then(function(){
              $state.go('view_albums');
            });
        }
      }

      $scope.select_file = function(files){
        if (files.length > 0){
          $scope.cover_file = files[0];
        }
      }
    }])

  .controller('CreateAlbumController', [
    '$scope', '$state', function($scope, $state){
      $scope.album = {};
      $scope.album_created = function(val){
        $state.go('create_log', {'aid': val.album.id})
      }
    }])
