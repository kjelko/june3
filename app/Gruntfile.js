module.exports = function(grunt) {
  
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    clean: {
      startFresh: ['static/js/script.min.js'],
      cleanUp: ['<%= concat.dist.dest %>']
    },
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['static/js/*.js', 'static/js/**/*.js'],
        dest: 'static/js/script.js'
      }
    },
    uglify: {
		  options: {
        banner: '/* <%= grunt.template.today("yyyy-mm-dd") %> */\n'
		  },
		  build: {
		    files: {
          'static/js/script.min.js': ['<%= concat.dist.dest %>']
        }
		  }
	  },
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-sass');
  
  grunt.registerTask('default', [
    'clean:startFresh', 
    'concat', 
    'uglify', 
    'clean:cleanUp'
  ]);
};
