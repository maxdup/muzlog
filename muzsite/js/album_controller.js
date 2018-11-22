require('ng-file-upload');
module.exports = angular.module('muz.albumCtrl', ['ngFileUpload'])

  .controller('ViewAlbumsController', [
    '$scope', 'Album', function($scope, Album) {
      Album.get().$promise.then(function(value){
        $scope.albums = value.albums;
      });
    }])

  .controller('EditAlbumController', [
    '$state', '$stateParams', '$scope', 'Album', 'Upload', '$q', 'conf',
    function($state, $stateParams, $scope, Album, Upload, $q, conf) {
      $scope.conf = conf;

      Album.get({id:$stateParams.id})
        .$promise.then(function(value){
          $scope.album = value.album;
        });

      $scope.save_changes = function(){
        Album.update($scope.album)
          .$promise.then(function(value){
            if ($scope.cover_file){
              upload($scope.cover_file, value.album.id)
                .then(function(result){
                  $scope.album = result.album;
                  $state.go('create_log', {'id': value.album.id});
                }, function(){
                  $state.go('create_log', {'id': value.album.id});
                })
              $scope.album = value.album;
            } else {
              $scope.album = value.album;
              $state.go('create_log', {'id': value.album.id});
            }
          })
      }
      $scope.cancel_changes = function(){
        $state.go('create_log', {'id': $scope.album.id});
      }

      $scope.delete_album = function(){
        if (confirm("This album will be deleted")){
          Album.delete({id:$scope.album.id})
            .$promise.then(function(){
              $state.go('admin');
            });
        }
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
      };

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