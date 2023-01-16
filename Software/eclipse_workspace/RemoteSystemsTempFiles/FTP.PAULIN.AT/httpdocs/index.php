<?php
/**
 * Part of Showkase web site management package
 *
 * @package Showkase
 * @author Jack Hardie {@link http://www.jhardie.com}
 * @copyright Copyright (c) 2013, SimpleViewer Inc.
 */
@error_reporting(E_ERROR);
@ini_set('display_errors', 1);
@ini_set('html_errors', 1);
try {
    $homePage = new HomePage();
    $homePath = $homePage->getHomePath();
    if ($homePath === false) {
        exit($homePage->getTempHomePageHtml());
    }
} catch (Exception $e) {
    print '
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Showkase Error</title>
<body>
  <h1>Showkase Error</h1>
  <p>'.$e->getMessage().'</p>
</body>
</html>
';
exit(0);
}
include $homePath;

/**
 * Manage home page paths and redirects
 */
Class HomePage {
    /**
     * @var boolean site is setup
     */
    private $setup = true;
    
    /**
     * @ var string absolute or relative url for showkase admin
     * Used for links when no home page
     */
    private $showkaseUrl;

    /**
     * @var string site content path from server root
     *
     */
    private $absContentPath;
    
    /**
     * @var string absolute path from server root to pages data
     * Used to find home page in pagesData
     */
    private $pagesDataPath;
    
    /**
     * Constructor
     *
     */
    public function __construct()
    {
        $rootConfigFile = 'showkaseconfig.ini';
        $this->pagesDataPath = '_data'.DIRECTORY_SEPARATOR.'pagesdata.txt';
        $this->absContentPath = getcwd();
        switch (true) {
            case is_dir('admin') :
                // we are in the site directory == installation directory
                $this->showkaseUrl = 'admin';
                break;
            case is_dir('../admin') :
                // we are in the site directory == subdirectory of installation directory
                $this->showkaseUrl = '../admin';
                break;
            case file_exists($rootConfigFile) :
                // we are not in the site directory but we have a root config file
                $config = parse_ini_file($rootConfigFile);
                if (count($config) < 3) {
                   throw new Exception('Error: cannot read the Showkase configuration file '.$rootConfigFile);
                }
                $this->showkaseUrl = $config['showkaseUrl'];
                $this->absContentPath = $config['absoluteContentPath'];
                $this->pagesDataPath = $config['absoluteContentPath'].DIRECTORY_SEPARATOR.$this->pagesDataPath;
                break;
            default :
                // we are not in the site directory and can't find the root config file
                throw new Exception('Error: cannot find the Showkase configuration file '.$rootConfigFile);
        }   
    }
    
    /**
     * Get absolute home page path
     * Home page cannot be a link
     * Home page cannot be a child page unless it is the first child of a link
     *
     * @return mixed string or false for no home page
     */
    public function getHomePath()
    {
        // N.B. is_readable not working on some Windows servers
        if (!file_exists($this->pagesDataPath)) return false;
        $contents = file_get_contents($this->pagesDataPath);
        if ($contents === false) {
            throw new Exception('Error: cannot read the Showkase pages data file '.basename($this->pagesDataPath));
        }
        $rawData = unserialize($contents);
        if (!is_array($rawData)) {
            throw new Exception('Error: cannot unserialize the Showkase pages data file '.basename($this->pagesDataPath));
        }
        if (count($rawData) == 0) return false;
        $weights = array();
        $isChild = array();
        $validParents = array();
        $pagesData = array();
        foreach ($rawData as $key=>$pageData) {
            $ref = 'r'.$pageData['pageRef'];
            $pagesData[$ref] = $pageData;
            if (!isset($pageData['parentPage'])) $pagesData[$ref]['parentPage'] = 0;
            if (!isset($pageData['navWeight']))  $pagesData[$ref]['navWeight'] = 0;
            if (!isset($pageData['navShow']))    $pagesData[$ref]['navShow'] = 'true';
            if (!isset($pageData['supported']))  $pagesData[$ref]['supported'] = 'true';
            $weights[] = $pageData['navWeight'];
            $isChild[] = ($pageData['parentPage'] != 0);
            if (
                $pageData['parentPage'] != 0
                && $pageData['pageType'] != 'link'
            ) {
                $validParents['r'.$pageData['parentPage']] = true;
            }
        }
        unset($key, $pageData, $rawData);
        // parents must come first
        array_multisort($isChild, $weights, $pagesData);
        $homePath = '';
        $homeParent = null;
        foreach ($pagesData as $ref => $pageData) {
            $foundHomePage = (
                is_null($homeParent)
                && $pageData['navShow']    == 'true'
                && $pageData['supported']  == 'true'
                && $pageData['pageType']   != 'link'
                && $pageData['parentPage'] == 0
            );
            $foundHomeChild = (
                !is_null($homeParent)
                && $pageData['navShow']        == 'true'
                && $pageData['supported']      == 'true'
                && $pageData['pageType']       != 'link'
                && 'r'.$pageData['parentPage'] == $homeParent
            );
            if ($foundHomePage || $foundHomeChild) {
                $homePath = $pageData['path'];
                break;
            }
            if (
                is_null($homeParent)
                && $pageData['pageType']         == 'link'
                && isset($validParents[$ref])
                && $pagesData[$ref]['navShow']   == 'true'
                && $pagesData[$ref]['supported'] == 'true'
            ) {
                //found parent of home page
                $homeParent = $ref;
            }
        }
        if ($homePath == '') return false;
        $homeFolder = basename(rtrim($homePath,'\\/'));
        // $this->absContentPath could be a simple slash
        return
            rtrim($this->absContentPath, '\\/').DIRECTORY_SEPARATOR.
            $homeFolder.DIRECTORY_SEPARATOR.
            'index.html';
    }
    
    /**
     * Get html for no home page
     *
     * @return string
     */
    public function getTempHomePageHtml()
    {
        $warningHtml = $this->showkaseUrl == ''
          ? '
    <p style="color: #CC2707">Error: cannot read the showkase config file.</p>'
          : '';
        return <<<EOD
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Showkase</title>
  <style type="text/css">
    body {
      font-family: arial, helvetica, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      color: #333333;
      background: #CCCCCC url(http://www.jhardie.com/sk-resources/showkaseweblogo.png) 56px 50px no-repeat;
    }
    #wrapper {
    margin: 120px 0 0 50px;
    border-radius: 10px;
    -webkit-box-shadow: 0 5px 5px 1px #666666;
    -moz-box-shadow: 0 5px 5px 1px #666666;
    box-shadow: 0 5px 5px 1px #666666;
    width: 360px;
    padding: 38px 46px 44px 46px;
    background: #FDF5D9;
    }
    h1 {
      font-size: 16px;
    }
    a:link, a:visited, a:hover {
      color: #24AAE0;
  </style>
</head>
<body>
  <div id="wrapper">
    <h1>Welcome to your New Showkase Web Site</h1>
    <p>This is a temporary home page. To manage your site sign-in to <a href="{$this->showkaseUrl}" target="_blank">Showkase Admin</a>.</p>
    {$warningHtml}
  </div>
</body>
</html>
EOD;
    }
} 
