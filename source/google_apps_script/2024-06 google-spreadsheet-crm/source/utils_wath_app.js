const WHAPI_BASE_URL = "https://gate.whapi.cloud/";

function extractFileId(url) {
  /*
  https://drive.google.com/file/d/1a2kWw90MbKjYy207-DcRrarL1_V2j_Eu/view?usp=drive_link ->
  1a2kWw90MbKjYy207-DcRrarL1_V2j_Eu
   */

  // search drive.google.com/file/d prefix using regex
  const regex = /drive.google.com\/file\/d\/([^\/]+)\//;
  const match = url.match(regex);
  if (match) {
    return match[1];
  } else {
    return null;
  }
}

function getGroups(offset, limit) {
  const url = WHAPI_BASE_URL + "groups?offset=" + offset + "&count=" + limit;
  const options = {
    method: "get",
    headers: {
      Authorization: "Bearer " + WHAPI_ADMIN_TOKEN,
      Accept: "application/json",
    },
  };
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  return data;
}

function getInviteAPI({ groupID }) {
  const url = WHAPI_BASE_URL + "groups/" + groupID + "/invite";
  const options = {
    method: "get",
    headers: {
      Authorization: "Bearer " + WHAPI_ADMIN_TOKEN,
      Accept: "application/json",
    },
  };
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  return data;
}

function addInGroup({ invite_code }) {
  let body;
  let url = WHAPI_BASE_URL + "groups/";

  body = { invite_code: invite_code };

  let options = {
    method: "put",
    headers: {
      Authorization: "Bearer " + WHAPI_ADMIN2_TOKEN,
      Accept: "application/json",
    },
    payload: JSON.stringify(body),
    contentType: "application/json",
  };

  return UrlFetchApp.fetch(url, options);
}

function post_event({ text, image_url: image_url, channel_id: channel_id }) {
  console.log("post_event", text.slice(0, 64), image_url, channel_id);
  let body;
  let url = WHAPI_BASE_URL + "messages/";
  if (image_url == "") {
    body = {
      to: channel_id,
      body: text,
    };
    url += "text";
  } else {
    let fileID = extractFileId(image_url);
    let blob = DriveApp.getFileById(fileID).getBlob();

    let contentType = blob.getContentType();
    let base64String = Utilities.base64Encode(blob.getBytes());
    // if

    // let blob = UrlFetchApp.fetch(imageUrl).getBlob()

    if (contentType === "application/pdf") {
      body = {
        to: channel_id,
        media: `data:application/pdf;base64,${base64String}`,
        caption: text,
        // "filename" : 'test'
      };
      url += "document";
    } else {
      body = {
        to: channel_id,
        media: `data:image/png;base64,${base64String}`,
        caption: text,
      };
      url += "image";
    }
  }

  let options = {
    method: "post",
    headers: {
      Authorization: "Bearer " + WHAPI_ADMIN2_TOKEN,
      Accept: "application/json",
    },
    payload: JSON.stringify(body),
    contentType: "application/json",
  };

  return UrlFetchApp.fetch(url, options);
}
