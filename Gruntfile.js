module.exports = function(grunt) {
  
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    clean: {
      startFresh: ['app/static/js/script.min.js'],
      cleanUp: ['app/static/js/script-concat.min.js']
    },
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['app/static/js/*.js', 'app/static/js/**/*.js'],
        dest: 'app/static/js/script-concat.min.js'
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
      scripts: {
        files: ['app/static/js/*.js', 'app/static/js/**/*.js', '!**/*.min.js'],
        tasks: ['clean:startFresh', 'concat', 'uglify', 'clean:cleanUp'],
        options: {
          interrupt: false
        }
      }
    },
    concurrent: {
      watch: {
        tasks: ['watch:styles', 'watch:scripts']
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-concurrent');

  grunt.registerTask('default', [
    'sass',
    'clean:startFresh', 
    'concat', 
    'uglify', 
    'clean:cleanUp',
    'concurrent'
  ]);
};
