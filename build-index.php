#!/usr/bin/php

<?php

if($argc != 3) {
    echo "Usage: {$argv[0]} docset version\n";
    return 0;
}

// prepare the docset sqlite database
$dsidx = "{$argv[1]}/Contents/Resources/docSet.dsidx";
@unlink($dsidx);
$sqlite = new Sqlite3($dsidx);
$sqlite->exec('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)');
$sqlite->exec('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)');
$stmt = $sqlite->prepare('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (:name, :type, :path)');


// parse the tokens for index
$reader = new XMLReader();
$reader->open("{$argv[1]}/Contents/Resources/Documents/api/Tokens.xml", 'UTF-8');
$count = 0;

// only these type are acceptable and map to Dash type
$types = ['macro' => 'Macro', 'func' => 'Function', 'tdef' => 'Type', 'econst'=>'Enum', 'cl' => 'Struct', 'instm'=>'Method'];
$folder = "{$argv[1]}/Contents/Resources/Documents/api/";
$alltypes = [];

while($reader->read()) {
    if($reader->name == "Token") {
        $xml = new SimpleXMLElement($reader->readOuterXml());

        if($xml->count() == 0)
            continue;

        $type = (string)$xml->TokenIdentifier->Type;
        $alltypes[$type] = 1;
        if(!isset($types[$type]) || !file_exists("${folder}{$xml->Path}"))
            continue;

        $name = (string)$xml->TokenIdentifier->Name;
        $path = "api/{$xml->Path}";
        if($xml->Anchor != '')
            $path .= "#{$xml->Anchor}";

        $stmt->bindValue(':name', $name, SQLITE3_TEXT);
        $stmt->bindValue(':type', $types[$type], SQLITE3_TEXT);
        $stmt->bindValue(':path', $path, SQLITE3_TEXT);
        $stmt->execute();

        if($count++ > 0 && $count % 1000 == 0)
            print "Processed {$count} Tokens\n";
    }
}


// parse the guide and add sections
$skip_guides = ['ffmpeg.html', 'ffplay.html', 'ffprobe.html', 'ffserver.html'];
foreach (glob("{$argv[1]}/Contents/Resources/Documents/*.html") as $guide) {
    if(array_search(basename($guide), $skip_guides) !== false)
        continue;
    
    $content = file_get_contents($guide);
    $pattern = PHP_OS == 'Darwin' ? '|<h1 class="titlefont">(.*)</h1>|' : '|<h1 class="settitle">(.*)</h1>|';
    if(preg_match($pattern, $content, $match) && count($match) == 2) {
        $guideFile = basename($guide);
        $stmt->bindValue(':name', $match[1], SQLITE3_TEXT);
        $stmt->bindValue(':type', 'Guide', SQLITE3_TEXT);
        $stmt->bindValue(':path', $guideFile, SQLITE3_TEXT);
        $stmt->execute();
        print("Processed Guide {$match[1]} => {$guideFile}.\n");
    }

    preg_match_all('|<a.*#toc-.*">(.*)</a>|', $content, $match);
    $search = [];
    $replace = [];
    $name_replace = ['<code>', '</code>'];
    foreach ($match[0] as $index => $subject) {
        $search[] = $subject;
        $name = str_replace($name_replace, '', $match[1][$index]);
        $replace[] = '<a class="dashAnchor" name="//apple_ref/Section/' . rawurlencode(html_entity_decode($name, ENT_HTML5, 'UTF-8')) . '"></a>' . $subject;
    }

    file_put_contents($guide, str_replace($search, $replace, $content));
    $guide = basename($guide);
    
}
$stmt->close();

$result = $sqlite->query('select count(*) as count, type from searchIndex group by type');
while($row = $result->fetchArray(SQLITE3_ASSOC))
    print("There are {$row['count']} entries in {$row['type']}.\n");

$sqlite->close();
