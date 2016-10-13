#!/usr/bin/php
<?php

if($argc != 3) {
	echo "Usage: {$argv[0]} which version.";
	exit();
}

$pwd = getcwd();
$dash = realpath("../Dash-User-Contributions/docsets");
if(!is_dir($dash)) {
	echo "Dash-User-Contributions folder doesn't exist.";
	exit();
}

if(!is_dir("{$argv[1]}/{$argv[2]}")) {
	echo "Don't know how to publish {$argv[1]}/{$argv[2]}.";
	exit();
}

$name = $argv[1] == 'ffmpeg' ? 'FFmpeg' : 'Libav';
$tarball = "{$argv[1]}/{$argv[2]}/{$name}.tgz";
$target = "{$dash}/{$name}/versions/{$argv[2]}";

if(!is_dir($target))
	mkdir($target, 0755, true);

copy($tarball, "$target/{$name}.tgz");

$json = json_decode(file_get_contents("{$dash}/{$name}/docset.json"));
$versions = [];
$remove = [];

foreach ($json->specific_versions as $version) {
	$versions[$version->version] = $version;
}

if(!isset($versions[$argv[2]])) {
	$version = new stdClass();
	$version->version = $argv[2];
	$version->archive = "versions/{$argv[2]}/{$name}.tgz";
	$versions[$argv[2]] = $version;
}

krsort($versions);

$json->specific_versions = [];
$major_versions = [];
foreach ($versions as $ver => $version) {
	$ver = substr($ver, 0, strrpos($ver, '.'));
    if(!isset($major_versions[$ver])) {
        $json->specific_versions[] = $version;
        $major_versions[$ver] = true;
    } else {
        print "Removing old version {$version->version}\n";
        $folder = "{$dash}/{$name}/";
        @unlink($folder . $version->archive);
        @rmdir(dirname($version->archive));
    }
}

$json->version = array_keys($versions)[0];
$json->archive = "{$name}.tgz";
$json->name = $name;
$json->author->name = "Steve Yin";
$json->author->link = "https://github.com/steve3d/Dash-Docset-FFmpeg";
file_put_contents("{$dash}/{$name}/docset.json", json_encode($json, JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES));
$readme = file_get_contents('README-docset.md');
file_put_contents("{$dash}/{$name}/README.md", str_replace(':NAME:', $name, $readme));
@unlink("{$dash}/{$name}/$name.tgz");
copy("{$dash}/{$name}/versions/{$json->version}/{$name}.tgz", "{$dash}/{$name}/$name.tgz");

echo "{$name}.docset {$argv[2]} are published.\n";

