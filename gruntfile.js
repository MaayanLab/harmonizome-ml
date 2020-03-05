module.exports = function(grunt) {
	grunt.initConfig({
		browserify: {
			scripts: {
				src: ['scripts/app.js'],
				dest: 'app/static/scripts/custom-predictions-page.js',
				options: {
					browserifyOptions: {
						standalone: 'app',
					},
					transform: [
						[
							"babelify", {
								"presets": ["env"]
							}
						]
					]
				}
			}
		},
		copy: {
			main: {
				files: [
					{
						expand: true,
						cwd: 'static',
						src: ['**/*'],
						dest: 'app/static'
					}
				]
			}
		},
		less: {
			"default": {
				options: {
					yuicompress: true
				},
				files: [
					{
						expand: true,
						cwd: './styles',
						src: ['*.less'],
						dest: 'app/static/styles',
						ext: '.css'
					}
				]
			}
		},
		watch: {
			copystuff: {
				files: ['./static/**/*'],
				tasks: ['copy']
			},
			bundlescripts: {
				files: ['./scripts/**/*'],
				tasks: ['browserify']
			},
			bundlestyle: {
				files: ['./styles/**/*'],
				tasks: ['less']
			},
			nodedeps: {
				files: ['./package.json'],
				tasks: ['shell:npmdeps']
			},
			pystuff: {
				files: [
					'./app/**/*',
					'!./app/static/**/*'
				],
				tasks: ['shell:ipynb']
			},
			pydeps: {
				files: ['app/requirements.txt'],
				tasks: ['shell:pydeps']
			}
		},
		shell: {
			flask: {
				command: 'python3 run.py',
				options: {
					async: true,
				},
			},
			flaskApp: {
				command: 'python3 run.py',
				options: {
					async: false,
				},
			},
			uwsgi: {
				command: 'uwsgi --ini app/uwsgi.ini',
				options: {
					async: false,
				}
			},
			ipynb: {
				command: 'python3 run.py preprocess',
				options: {
					async: false,
				}
			},
			pydeps: {
				command: 'pip3 install -r app/requirements.txt',
				options: {
					async: false,
				}
			},
			npmdeps: {
				command: 'npm install',
				options: {
					async: false
				}
			},
			options: {
				stdout: true,
				stderr: true,
				failOnError: true
			}
		}
	})

	grunt.loadNpmTasks('grunt-browserify')
	grunt.loadNpmTasks('grunt-contrib-copy')
	grunt.loadNpmTasks('grunt-contrib-less')
	grunt.loadNpmTasks('grunt-contrib-watch')
	grunt.loadNpmTasks('grunt-shell-spawn')
	grunt.loadNpmTasks('grunt-continue')

	grunt.registerTask('prepare', [
		'shell:pydeps',
	])
	grunt.registerTask('build', [
		'shell:ipynb',
		'less',
		'copy',
		'browserify'
	])
	grunt.registerTask('start', [
		'build',
		'watch',
	])
	grunt.registerTask('start:flask', [
		'shell:flask',
		'build',
		'continue:on',
		'watch',
		'continue:off',
		'shell:flask:kill',
	])
	grunt.registerTask('start:flaskApp', [
		'shell:flaskApp',
	])
	grunt.registerTask('start:uwsgi', [
		'build',
		'shell:uwsgi',
	])
}