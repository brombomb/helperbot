<?php
$urlfile = 'urls.txt';
$file = fopen($urlfile, 'r');
while(($link = fgets($file)) !== false) {
    if(empty($urls[$link])) {
        $urls[$link] = true;
        $linksHtml .= '<li><a href="'. $link. '">'. $link. '</a></li>';
    }
}
fclose($file);
$linklastmod = date("F d, Y g:i A.", filemtime($urlfile));

$songfile = 'spotify.txt';
$file = fopen($songfile, 'r');
while(($link = fgets($file)) !== false) {
    if(empty($songs[$link])) {
        $songs[$link] = true;
        $songsHtml .= '<li><a href="'. $link. '">'. $link. '</a></li>';
    }
}
fclose($file);
$songlastmod = date("F d, Y g:i A.", filemtime($songfile));

?>

<html>
<head>
<title>10100 Links & Songs</title>
</head>
<body>

    <h1>Links</h1>
    <ul>
    <?php echo $linksHtml; ?>
    </ul>
    <em>Last Modified: <?php echo $linklastmod; ?></em>

    <h1>Songs</h1>
    <ul>
    <?php echo $songsHtml; ?>
    </ul>
    <em>Last Modified: <?php echo $songlastmod; ?></em>

</body>
</html>
