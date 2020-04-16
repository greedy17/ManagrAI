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
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

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
  height: 1.5rem;
  width: 1.5rem;
  border-radius: 50%;
}

.contact-name {
  margin-left: auto;
  width: 25%;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $main-font-gray;
}

.contact-email-container {
  width: 50%;
  height: 1.5rem;
  padding: 0.125rem;
  background-color: $soft-gray;
  border-radius: 5px;
  margin-left: auto;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.email-icon {
  height: 1rem;
  width: 1rem;
  margin-left: 0.375rem;
}

.contact-email {
  margin-left: 0.375rem;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 10px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $main-font-gray;
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
  padding: 0.125rem;
  margin-bottom: 2%;
}

.template-variable {
  @include pointer-on-hover();
  border-radius: 100px;
  background-color: $theme-gray;
  margin-right: auto;
  width: 6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 10px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.6;
  letter-spacing: normal;
  height: 1.5rem;
  color: rgba($color: $main-font-gray, $alpha: 0.5);
}

.example {
  margin-right: unset;
  padding: 0.125rem 0;
  display: inline-block;
  height: 1rem;
  width: 4.5rem;
  text-align: center;
  vertical-align: center;
}

.template-selector-container {
  display: flex;
  flex-flow: row;
  height: 1.5rem;
  align-items: center;
}

.template-selector-label {
  width: 25%;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $main-font-gray;
}

.template-selector-dropdown {
  @include pointer-on-hover();
  width: 50%;
  height: 1.5rem;
  padding: 0.125rem;
  background-color: $soft-gray;
  border-radius: 5px;
  margin-right: auto;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.selected-template-name {
  margin-left: 5%;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.dropdown-arrow-icon {
  margin-left: auto;
  margin-right: 5%;
}

input {
  @include input-field();
  height: 2.5rem;
  margin-top: 2%;
}

.email-content {
  margin: 1% 0 2% 0;
  flex-grow: 1;
  border-radius: 4px;
  border: solid 1px $soft-gray;
  background-color: $white;
  padding: 1vh;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 12px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: rgba($color: $base-gray, $alpha: 0.5);

  &:focus {
    box-shadow: 0 0 10px rgba($color: $dark-green, $alpha: 0.5);
    outline: none;
    background-color: $white;
  }
}

.send-button-container {
  display: flex;
  flex-flow: row;
}

.send-button {
  @include primary-button();
  margin-left: auto;
}
</style>
