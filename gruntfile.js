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
				command: 'python ./main.py',
				options: {
					async: true,
					execOptions: {
						cwd: './app'
					}
				},
			},
			flaskApp: {
				command: 'python ./main.py',
				options: {
					async: false,
					execOptions: {
						cwd: './app'
					}
				},
			},
			uwsgi: {
				command: 'uwsgi --ini ./uwsgi.ini',
				options: {
					async: false,
					execOptions: {
						cwd: './app'
					}
				}
			},
			ipynb: {
				command: 'python ./preprocess.py',
				options: {
					execOptions: {
						async: false,
						cwd: './app'
					}
				}
			},
			pydeps: {
				command: 'pip install -r requirements.txt',
				options: {
					execOptions: {
						async: false,
						cwd: './app'
					}
				}
			},
			npmdeps: {
				command: 'npm install',
				options: {
					execOptions: {
						async: false
					}
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
		'watch',
		'shell:flask:kill'
	])
	grunt.registerTask('start:uwsgi', [
		'build',
		'shell:uwsgi',
	])
}