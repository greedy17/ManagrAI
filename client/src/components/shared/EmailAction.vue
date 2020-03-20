<template>
  <div class="email-action">
    <div class="email-top-section">
      <div class="contacts-container">
        <div class="contact">
          <img class="contact-img" src="@/assets/images/sara-smith.png" alt="contact image" />
          <span class="contact-name">Sara Smith</span>
          <div class="contact-email-container">
            <img class="email-icon" src="@/assets/images/email.svg" alt="email icon" />
            <span class="contact-email">sara@samsung.com</span>
          </div>
        </div>
        <div class="contact">
          <img class="contact-img" src="@/assets/images/jake-murray.png" alt="contact image" />
          <span class="contact-name">Jake Murray</span>
          <div class="contact-email-container">
            <img class="email-icon" src="@/assets/images/email.svg" alt="email icon" />
            <span class="contact-email">jake@samsungmedia.com</span>
          </div>
        </div>
      </div>
      <div class="email-template-tools">
        <div class="template-variables-container">
          <span class="template-variable">First Name</span>
          <span class="template-variable">Last Name</span>
          <span class="template-variable">Company</span>
        </div>
        <div class="template-selector-container">
          <span class="template-selector-label">Email Template:</span>
          <div class="template-selector-dropdown">
            <span class="selected-template-name">Template 1</span>
            <img
              class="dropdown-arrow-icon"
              src="@/assets/images/dropdown-arrow.svg"
              alt="dropdownn arrow icon"
            />
          </div>
        </div>
      </div>
    </div>
    <input class="email-subject" placeholder="Call Friday?" />
    <div class="email-content" contenteditable="true">
      Hi <span class="template-variable example">First Name</span> , <br /><br />

      Hope all is well today! Just following up to see if you have time to chat Friday about our
      demo! Looking forward to syncing up about our product for a March start date. <br /><br />

      Joe
    </div>
    <div class="send-button-container">
      <span class="send-button">Send</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmailAction',
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

.email-action {
  width: 100%;
  display: flex;
  flex-flow: column;
}

.email-top-section {
  display: flex;
  flex-flow: row;
}

.contacts-container {
  display: flex;
  flex-flow: column;
  width: 40%;
  padding-right: 3%;
}

.contact {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 2%;
}

.contact-img {
  height: 24px;
  width: 24px;
  border-radius: 50%;
}

.contact-name {
  margin-left: auto;
  width: 25%;
  font-family: Lato;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;
}

.contact-email-container {
  width: 50%;
  height: 24px;
  padding: 2px;
  background-color: #efeff5;
  border-radius: 5px;
  margin-left: auto;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.email-icon {
  height: 16px;
  width: 16px;
  margin-left: 5px;
}

.contact-email {
  margin-left: 5px;
  font-family: Lato;
  font-size: 10px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;
}

.email-template-tools {
  flex-grow: 1;
  display: flex;
  flex-flow: column;
}

.template-variables-container {
  display: flex;
  flex-flow: row;
  align-items: center;
  padding: 2px;
  margin-bottom: 2%;
}

.template-variable {
  border-radius: 100px;
  background-color: #d7d7dd;
  margin-right: auto;
  width: 95px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Lato;
  font-size: 10px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.6;
  letter-spacing: normal;
  height: 24px;
  color: rgba($color: #110f24, $alpha: 0.5);

  &:hover {
    cursor: pointer;
  }
}

.example {
  margin-right: unset;
  padding: 2px 0;
  display: inline-block;
  height: 16px;
  width: 70px;
  text-align: center;
  vertical-align: center;
}

.template-selector-container {
  display: flex;
  flex-flow: row;
  height: 24px;
  align-items: center;
}

.template-selector-label {
  width: 25%;
  font-family: 'Lato', sans-serif;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;
}

.template-selector-dropdown {
  width: 50%;
  height: 24px;
  padding: 2px;
  background-color: #efeff5;
  border-radius: 5px;
  margin-right: auto;
  display: flex;
  flex-flow: row;
  align-items: center;

  &:hover {
    cursor: pointer;
  }
}

.selected-template-name {
  margin-left: 5%;
  font-family: Lato;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #110f24;
}

.dropdown-arrow-icon {
  margin-left: auto;
  margin-right: 5%;
}

input {
  height: 40px;
  border-radius: 4px;
  background-color: #fafafa;
  border: none;
  box-sizing: border-box;
  padding: 3%;
  margin-top: 2%;

  &:focus {
    box-shadow: 0 0 10px rgba($color: #199e54, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: 'Lato', sans-serif;
    font-size: 14px;
    font-weight: normal;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: #444444;
  }
}

.email-content {
  margin: 1% 0 2% 0;
  // height: 30%;
  flex-grow: 1;
  border-radius: 4px;
  border: solid 1px #ececee;
  background-color: #ffffff;
  padding: 1vh;
  font-family: 'Lato', sans-serif;
  font-size: 12px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: rgba($color: #444444, $alpha: 0.5);

  &:focus {
    box-shadow: 0 0 10px rgba($color: #199e54, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }
}

.send-button-container {
  display: flex;
  flex-flow: row;
}

.send-button {
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 15px;
  border-radius: 5px;
  background-color: #199e54;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #ffffff;

  &:hover {
    cursor: pointer;
  }
}
</style>
