
module.exports = angular.module('muz.adminCtrl', [])
  .controller('AdminController', [
    '$scope', 'Album', function($scope, Album) {
      Album.get().$promise.then(function(value){
        $scope.albums = value.albums;
        console.log($scope.albums);
      });
    }])
  .controller('EditAlbumController', [
    '$stateParams', '$scope', 'Album',
    function($stateParams, $scope, Album) {
      console.log('statep', $stateParams);
      Album.get({id:$stateParams}).$promise.then(function(value){
        $scope.albums = value.albums;
        console.log($scope.albums);
      });
    }]);
