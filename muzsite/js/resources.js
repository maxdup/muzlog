require('angular-resource/angular-resource.js');

module.exports = angular.module('muz.resources',['ngResource', 'ngFileUpload'])
  .factory('Album', ["$resource", function($resource) {
    return $resource( '/api/album/:id', {id: '@id'},
                      {'update':{ method:'PUT'}});
  }])
  .factory('Log', ["$resource", function($resource) {
    return $resource( '/api/log/:id', {id: '@id'},
                      {'update':{ method:'PUT'}});
  }])
  .factory('Profile', ["$resource", "ProfileInterceptor", function($resource, interceptor) {
    return $resource( '/api/profile/:id', {id: '@id'},
                      {'update':{ method:'PUT', interceptor: interceptor},
                       'me': { method:'GET',
                               url:'/api/profile/me',
                               interceptor: interceptor}});
  }])
  .factory('UserRoles', ["$resource", function($resource) {
    return $resource( '/api/roles/:id', {id: '@id'},
                      {'update':{ method:'PUT'}});
  }])
  .service('UploadService', ['$q', 'Upload', function($q, Upload){
    var upload = function(path, file){
      return $q(function(resolve, reject) {
        Upload.upload({
          'url': path,
          'data': { 'file': file }})
          .then(resolve,reject);
      })
    }
    return {upload: upload}
  }])

  .factory('ProfileInterceptor', ["$rootScope", function($rootScope) {
  return {
    response: function(response){

      if (response.config.method == 'PUT' ||
          response.config.method == 'POST'){
        if (response.status == 200 && response.data.profile &&
            response.data.profile.id == $rootScope.profile.id){
          $rootScope.profile = response.data.profile;
        }
      }
      if (response.config.method == 'GET'){
        if (response.status == 200 && response.data.profile){
          if (response.config.url == '/api/profile/me' ||
              response.data.profile.id == $rootScope.profile.id){
            $rootScope.profile = _.cloneDeep(response.data.profile);
          }
        }
      }
      return response.data;
    }
  }
}])
