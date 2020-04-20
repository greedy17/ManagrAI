<template>
  <div class="call-action">
    <div class="call-action-left-pane">
      <div class="contacts-container">
        <div class="contact">
          <img class="contact-img" src="@/assets/images/sara-smith.png" alt="contact image" />
          <span class="contact-name">Sara Smith</span>
          <div class="contact-phone-number-container">
            <img class="telephone-icon" src="@/assets/images/telephone.svg" alt="telephone icon" />
            <span class="contact-phone-number">555-555-5555</span>
          </div>
        </div>
        <div class="contact">
          <img class="contact-img" src="@/assets/images/jake-murray.png" alt="contact image" />
          <span class="contact-name">Jake Murray</span>
          <div class="contact-phone-number-container">
            <img class="telephone-icon" src="@/assets/images/telephone.svg" alt="telephone icon" />
            <span class="contact-phone-number">555-555-5555</span>
          </div>
        </div>
      </div>
      <div class="details-container">
        <input placeholder="Title" />
        <input :placeholder="date" />
      </div>
    </div>
    <div class="call-action-right-pane">
      <div class="text-area-container">
        <textarea placeholder="Detail" />
      </div>
      <div class="save-button-container">
        <span class="save-button">Save</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallAction',
  computed: {
    date() {
      let today = new Date()
      let dd = String(today.getDate()).padStart(2, '0')
      let mm = String(today.getMonth() + 1).padStart(2, '0') //January is 0!
      let yyyy = today.getFullYear()
      return mm + '/' + dd + '/' + yyyy
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.call-action {
  width: 100%;
  display: flex;
  flex-flow: row;
}

/* left pane below */
.call-action-left-pane {
  width: 40%;
  padding-right: 3%;
  display: flex;
  flex-flow: column;
}

.contacts-container {
  display: flex;
  flex-flow: column;
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

.contact-phone-number-container {
  @include pointer-on-hover();
  width: 50%;
  height: 1.5rem;
  padding: 0.125rem;
  margin-left: auto;
  background-color: $soft-gray;
  border-radius: 5px;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.telephone-icon {
  height: 1rem;
  width: 1rem;
  margin-left: 0.375rem;
}

.contact-phone-number {
  margin-left: 0.375rem;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $main-font-gray;
}

.details-container {
  margin-top: 3%;
  display: flex;
  flex-flow: column;
}

input {
  @include input-field();
  height: 2.5rem;
  margin: 0.375rem 0;
}

/* right-pane below */
.call-action-right-pane {
  flex-grow: 1;
  display: flex;
  flex-flow: column;
}

.text-area-container {
  height: 95%;
  display: flex;
  align-items: top;
  justify-content: center;
}

textarea {
  @include input-field();
  resize: none;
  height: 94%;
  width: 100%;
  font-size: 14px;
}

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  @include primary-button();
  margin-left: auto;
}
</style>
