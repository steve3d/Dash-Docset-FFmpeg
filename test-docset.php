#!/usr/bin/php

<?php

function testDocset($folder, $name, $pwd) {
	echo "Now testing {$folder}/{$name}.docset\n";
	chdir($folder);
	$cwd = getcwd();
	system("tar zxf {$name}.tgz");
	chdir("{$name}.docset/Contents/Resources");
	$sqlite = new SQLite3('docSet.dsidx');

	echo "Searching for missing index entries: {$folder} \n";
	// clean up the index for missing pages
	$result = $sqlite->query('select * from searchIndex');
	$missingId = [];
	while($row = $result->fetchArray(SQLITE3_ASSOC)) {
	    $path = "Documents/{$row['path']}";
	    $path = explode('#', $path)[0];
	    if(!file_exists($path)) {
	    	$missingId[] = $row['id'];
	        echo "{$path} missing.\n";
	    }
	}

	if(count($missingId) == 0)
		echo "Docset: {$folder} passed test.\n";

	$guides = 0;
	$result = $sqlite->query('select * from searchIndex where type="Guide"');
	while($row = $result->fetchArray(SQLITE3_ASSOC))
		$guides ++;

	if($guides == 0)
		print("There is no guides included.\n");

	$sqlite->close();
	chdir($cwd);
	@system("rm -rf {$name}.docset");
	chdir($pwd);
}

$pwd = getcwd();
if($argc == 3) {
	if(is_dir("$argv[1]/$argv[2]")) {
		$name = $argv[1] == 'ffmpeg' ? 'FFmpeg' : 'Libav';
		testDocset("$argv[1]/$argv[2]", $name, $pwd);
	} else {
		echo "Can not open folder $argv[1]/$argv[2].\n";
	}

	exit();
} else if($argc != 1) {
	echo "Usage: {$argv[0]} [which] [version]";
	exit();
}

foreach (['FFmpeg', 'Libav'] as $name) {
	$folder = strtolower($name);
	if(!is_dir($name))
		continue;

	foreach(array_diff(scandir($folder), ['.', '..', '.DS_Store']) as $version) {
		testDocset("{$folder}/{$version}", $name, $pwd);
	}
}