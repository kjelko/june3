module.exports = function(grunt) {
  
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    clean: {
      startFresh: ['app/static/js/script.min.js', 'app/static/css/style.min.css'],
      cleanUp: ['<%= concat.dist.dest %>']
    },
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['app/static/js/*.js', 'app/static/js/**/*.js'],
        dest: 'app/static/js/script.js'
      }
    },
    uglify: {
      options: {
        banner: '/* <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        files: {
          'app/static/js/script.min.js': ['<%= concat.dist.dest %>']
        }
      }
    },
    sass: {
      options: {
        style: 'compressed'
      },
      dist: {
        src: 'app/static/css/main.scss',
        dest: 'app/static/css/style.min.css',
      }
    },
    watch: {
      styles: {
        files: ['app/static/css/*.scss'],
        tasks: ['sass'],
      },
    },
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('default', [
    'clean:startFresh', 
    'concat', 
    'uglify', 
    'sass',
    'clean:cleanUp',
    'watch',
  ]);
};
