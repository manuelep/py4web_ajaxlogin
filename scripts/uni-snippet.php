<?php // Just an example snippet
$authhost = "http(s)://your.host";
$authapp = "infolayers2";
$url = "{$authhost}/{$authapp}/ajaxtoken";
$myid = get_current_user_id();
$mySecretB64Token = base64_encode("ThisIsAnInsecurePublicTokenDontUseIt");

$layerUrl = "{$authhost}/{$authapp}/testcall";

$data = [
    'user_id' => $myid,
	//'next' => $layerUrl
];
$json_data = json_encode($data);

$context = stream_context_create([
    'http' => [
        'method' => 'PUT',
        'header' => "Content-type: application/json\r\n" .
                    "Accept: application/json\r\n" .
                    "Connection: close\r\n" .
					"Authorization: Bearer {$mySecretB64Token}\r\n" .
                    "Content-length: " . strlen($json_data) . "\r\n",
        'protocol_version' => 1.1,
        'content' => $json_data
    ],
    'ssl' => [
        'verify_peer' => false,
        'verify_peer_name' => false
    ]
]);

$rawdata = file_get_contents($url, false, $context);
if ($rawdata === false) {
    exit("Unable to update data at $url");
}
$result = json_decode($rawdata, true);
if (JSON_ERROR_NONE !== json_last_error()) {
    exit("Failed to parse json: " . json_last_error_msg());
} else {
	$url_to_call = $result['url'];
};

//echo($result['url']);
?>
<script type="text/javascript">

	function call4layer() {
		fetch("<?php echo $layerUrl ?>", {
			keepalive: true,
			mode: 'cors',
			credentials: 'include',
			cache: 'no-cache',
		}).then(function (response) {response.json().then(function (data) {console.log(data)})})
	};

	<?php if ( $url_to_call ): ?>

	fetch("<?php echo $url_to_call ?>", {
		mode: 'cors',
	  	credentials: 'include',
		// cache: 'no-cache'
	}).then(function (response) {response.json().then(()=>{console.log('OK')})});

	<?php endif; ?>

</script>
