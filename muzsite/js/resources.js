require('angular-resource/angular-resource.js');

module.exports = angular.module('muz.resources',['ngResource'])
  .factory('Album', ["$resource", function($resource) {
    return $resource( '/api/album/:id', {id: '@id'},
                      {'update':{ method:'PATCH'}});
  }])
