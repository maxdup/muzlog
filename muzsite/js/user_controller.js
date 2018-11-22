require('ng-file-upload');
module.exports = angular.module('muz.userCtrl', [])

  .controller('ViewProfilesController', [
    "$scope", "Profile", function($scope, Profile){

      Profile.get().$promise.then(function(profiles){
        $scope.profiles = profiles.profiles;
      })
    }
  ])
  .controller('EditProfileController', [
    "$stateParams", "$scope", "Profile",
    function($stateParams, $scope, Profile){

      Profile.get({id:$stateParams.id})
        .$promise.then(function(value){
          $scope.profile = value.profile;
        });
    }
  ])
  .controller('EditRolesController', [
    "$scope", "Profile", function($scope, Profile){
      Profile.get().$promise.then(function(profiles){
        $scope.profiles = profiles.profiles;
      })
    }
  ])
