module.exports = angular.module('muz.logCtrl', [])
  .controller('CreateLogController', [
    '$stateParams', '$scope', 'Album', '$http',
    function($stateParams, $scope, Album, $http) {
      $scope.album = {};

      Album.get({'id': $stateParams.aid})
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

  .controller('ViewLogsController', [
    '$stateParams', '$scope', 'Log', '$http',
    function($stateParams, $scope, Log, $http) {

      Log.get().$promise.then(function(value){
        $scope.logs = value.logs;
        console.log('logs', $scope.logs);
      });
    }]);
