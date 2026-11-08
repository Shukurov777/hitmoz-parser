<?php
// No Python needed: just call the API
$api  = 'https://bakha.me/hitmoz';
$data = json_decode(file_get_contents($api . '/top?limit=10'), true);

foreach ($data['songs'] as $s) {
    echo "{$s['rank']}. {$s['artist']} — {$s['title']} [{$s['duration']}]\n{$s['download']}\n";
}
