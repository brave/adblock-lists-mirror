// ==UserScript==
// @name            Bypass Paywalls Clean - fi/se
// @version         4.1.8.1
// @description     Bypass Paywalls of news sites
// @author          magnolia1234
// @downloadURL     https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.fi.se.user.js
// @updateURL       https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.fi.se.user.js
// @homepageURL     https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters
// @supportURL      https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters
// @license         MIT; https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=LICENSE
// @match           *://*.berlingske.dk/*
// @match           *://*.dn.se/*
// @match           *://*.etc.se/*
// @match           *://*.suomensotilas.fi/*
// @match           *://*.weekendavisen.dk/*
// @connect         archive.fo
// @connect         archive.is
// @connect         archive.li
// @connect         archive.md
// @connect         archive.ph
// @connect         archive.vn
// @grant           GM.xmlHttpRequest
// @require         https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc_func.js
// ==/UserScript==

(function() {
  //'use strict';

window.setTimeout(function () {

if (matchDomain(['berlingske.dk', 'weekendavisen.dk'])) {
  let paywall = document.querySelector('div#paywall');
  if (paywall) {
    removeDOMElement(paywall);
    let article = document.querySelector('div[itemprop="articleBody"');
    if (article) {
      let intro = article.querySelector('p');
      let intro_class = intro ? intro.className : '';
      let json_script = document.querySelector('script#__NEXT_DATA__');
      if (json_script) {
        try {
          let json = JSON.parse(json_script.text);
          if (json && json.props.pageProps.article.body) {
            function getChildValue(child) {
              let value;
              if (child.children && child.children[0]) {
                if (child.children[0].value)
                  value = child.children[0].value;
                else if (child.children[0].children)
                  value = child.children[0].children[0].value;
              }
              return value;
            }
            article.innerHTML = '';
            let parser = new DOMParser();
            let pars = json.props.pageProps.article.body;
            for (let par of pars) {
              let elem = document.createElement('p');
              if (['ParagraphNode', 'HeadingNode'].includes(par.type)) {
                elem.className = intro_class;
                if (par.children) {
                  for (let child of par.children) {
                    let sub_elem;
                    if (child.type === 'TextNode') {
                      sub_elem = document.createElement('span');
                      sub_elem.innerText = child.value;
                      if (par.type === 'HeadingNode')
                        sub_elem.style = 'font-weight: bold;';
                    } else if (child.type === 'HyperlinkNode') {
                      let value = getChildValue(child);
                      if (child.url && value) {
                        sub_elem = document.createElement('a');
                        sub_elem.href = child.url;
                        sub_elem.innerText = value;
                      } else
                        console.log(child)
                    } else if (child.type === 'LineBreakNode') {
                      let sub_elem = document.createElement('br');
                    } else
                      console.log(child);
                    if (sub_elem)
                      elem.appendChild(sub_elem);
                  }
                }
              } else if (par.type === 'FigureNode') {
                if (par.asset && par.asset.image && par.asset.image.assets) {
                  let asset = par.asset.image.assets.pop();
                  if (asset && asset.url) {
                    let caption;
                    if (par.caption && par.caption[0]) {
                      caption = getChildValue(par.caption[0]);
                      if (par.byline && par.byline[0])
                        caption += ' ' + getChildValue(par.byline[0]);
                    }
                    let sub_elem = makeFigure(asset.url, caption, {style: 'width: 95%;'});
                    elem.appendChild(sub_elem);
                  }
                }
              } else if (par.type === 'ListNode') {
                let sub_elem = document.createElement('ul');
                if (par.children) {
                  for (let child of par.children) {
                    let value = getChildValue(child);
                    if (value) {
                      let li = document.createElement('li');
                      li.innerText = value;
                      sub_elem.appendChild(li);
                    }
                  }
                  elem.appendChild(sub_elem);
                }
              } else if (par.type === 'LineBreakNode') {
                let sub_elem = document.createElement('br');
                elem.appendChild(sub_elem);
              } else if (par.type === 'CustomCodeNode') {
                elem = document.createElement('div');
                if (par.code && !par.code.includes('newsletterSignupWidget')) {
                  let doc = parser.parseFromString('<div>' + par.code + '</div>', 'text/html');
                  let sub_elem = doc.querySelector('div');
                  elem.appendChild(sub_elem);
                }
              } else
                console.log(par);
              if (elem.hasChildNodes())
                article.appendChild(elem);
            }
          }
        } catch (err) {
          console.log(err);
        }
      }
    }
  }
  let ads = 'div[data-ad-banner]';
  hideDOMStyle(ads);
}

else if (matchDomain('dn.se')) {
  let url = window.location.href;
  getArchive(url, 'div.paywall-wrapper', '', 'article');
  let ads = 'div.bad';
  hideDOMStyle(ads);
}

else if (matchDomain('etc.se')) {
  let paywall = document.querySelector('section.prose-feature > section.teaser-section');
  if (paywall) {
    paywall.classList.remove('teaser-section');
    paywall.parentNode.querySelectorAll('.hidden').forEach(e => e.classList.remove('hidden'));
  }
  let ads = 'div[class$="-ad"], article section.font-sans';
  hideDOMStyle(ads);
  let video_iframes = document.querySelectorAll('div.embed-block > iframe[width][height]');
  for (let elem of video_iframes) {
    if (elem.width > 1000) {
      let ratio = elem.width / (mobile ? 320 : 640);
      elem.width = elem.width / ratio;
      elem.height = elem.height / ratio;
    }
  }
}

else if (matchDomain('suomensotilas.fi')) {
  let obscured = document.querySelector('div.epfl-pw-obscured');
  if (obscured)
    obscured.classList.remove('epfl-pw-obscured');
}

ads_hide();
leaky_paywall_unhide();

}, 1000);

// General Functions

// import (see @require)

})();
