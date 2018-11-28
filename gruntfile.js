module.exports = function(grunt){
  pkg: grunt.file.readJSON('package.json'),

  grunt.initConfig({
    concat: {
      base: {
        src: [
          'muzsite/static/lib/jquery/dist/jquery.min.js',
          //'muzsite/static/lib/lodash/dist/lodash.min.js',
          //'muzsite/static/lib/materialize/dist/js/materialize.min.js'
        ],
        dest: 'muzsite/static/js/base.js'
      },
      cms: {
        src: [
          'muzsite/js/admin.js',
          'muzsite/js/directives.js',
          'muzsite/js/resources.js',
          'muzsite/js/album_controller.js',
          'muzsite/js/user_controller.js',
          'muzsite/js/log_controller.js'
        ],
        dest: 'muzsite/static/js/cms.js'
      },
      angular: {
        src: [
          'muzsite/static/lib/angular/angular.min.js',
          //'muzsite/static/lib/angular-ui-router/release/angular-ui-router.min.js',
          //'muzsite/static/lib/angular-animate/angular-animate.min.js',
          //'muzsite/static/lib/angular-sanitize/angular-sanitize.min.js',
          //'muzsite/static/lib/angular-resource/angular-resource.min.js',
          //'muzsite/static/lib/ng-file-upload/ng-file-upload.min.js'
        ],
        dest: 'muzsite/static/js/angular.js'
      },
    },
    uglify: {
      options: {
        mangle: false
      },
      js : {
        files: {
          'muzsite/static/js/cms.min.js': ['muzsite/static/js/cms.js']
        }
      }
    },
    /*copy: {
      main: {
        files: [
          {expand: true,
           cwd: 'torres/static/bower_components/bootstrap/fonts/',
           src: ['*'],
           dest: 'torres/static/fonts/',
           filter: 'isFile'}
        ]
      }
    },*/
    watch :{
      main: {
        files: ['muzsite/js/*.js'],
        tasks: ['concat:base', 'uglify'],
      },
    }
  });
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.registerTask('build', ['concat']);
  grunt.registerTask('default', ['watch']);
};
