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
    "$scope", "Profile", "UserRoles",
    function($scope, Profile, UserRoles){

      Profile.get().$promise.then(function(profiles){
        $scope.profiles = profiles.profiles;
      })
      UserRoles.get().$promise.then(function(roles){
        $scope.roles = roles.roles
      })

      $scope.add_role = function(profile, role){
        UserRoles.save({'id': profile.id, 'role': role})
          .$promise.then(function(value){
            profile.roles = value.profile.roles;
          });
      }
      $scope.remove_role = function(profile, role){
        UserRoles.update({'id': profile.id, 'role': role})
          .$promise.then(function(value){
            profile.roles = value.profile.roles;
          });
      }

    }
  ])
