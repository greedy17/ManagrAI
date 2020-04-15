<template>
  <div class="lead">
    <div class="header">
      <span class="lead-name"> {{ lead.name }} </span>
      <div class="lead-description">
        <span>{{ lead.primaryNote }}</span>
        <span>{{ lead.secondaryNote }}</span>
      </div>
      <div class="contacts-container">
        <div v-for="contact in lead.contacts" :key="contact.id" class="contact">
          <img class="image" src="@/assets/images/sara-smith.png" alt="contact" />
          <span>{{ contact.name }} </span>
        </div>
      </div>
      <div class="button-container">
        <button v-if="isClaimed" @click="routeToRepPage">
          <img class="icon" alt="icon" src="@/assets/images/claimed.svg" />
          <span>{{ this.rep.name }}</span>
        </button>
        <button v-else @click="claimLead">
          <img class="icon" alt="icon" src="@/assets/images/add.svg" />
          <span>Claim</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
// TODO(Bruno 4-15-20): if no contacts, display so
// TODO(Bruno 4-15-20): if more than three contacts, display a ( + X )

const exampleReps = [
  { id: 1, name: 'Marcy Ewald' },
  { id: 2, name: 'Pari Baker' },
  { id: 3, name: 'Bruno Garcia Gonzalez' },
]

export default {
  name: 'Lead',
  props: ['lead'],
  data() {
    return {
      isClaimed: null,
      rep: null,
    }
  },
  created() {
    this.isClaimed = Math.floor(Math.random() * 2) == 0
    if (this.isClaimed) {
      this.rep = exampleReps[Math.floor(Math.random() * 3)]
    }
  },
  methods: {
    routeToRepPage() {
      alert('Clicking a rep name should route to the RepDetail')
    },
    claimLead() {
      alert(
        'Clicking claim should claim the lead and not change the page (so that many leads can be claimed in succession)',
      )
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.lead {
  margin-bottom: 0.625rem;
}

.lead,
.lead > * {
  font-family: $base-font-family, $backup-base-font-family;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.9rem;
}

.header {
  @include disable-text-select();
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 3rem;
  border: 2px solid $off-white;
}

.lead-name {
  @include pointer-on-hover();
  width: 20%;
  padding-left: 1%;
  height: 1rem;
  font-family: $base-font-family, $backup-base-font-family;
  font-weight: bold;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.lead-description {
  display: flex;
  flex-flow: column;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $main-font-gray;
  width: 20%;
}

.image {
  height: 1.4rem;
  width: 1.4rem;
  border-radius: 50%;
  margin-right: 1rem;
}

.icon {
  height: 1.4rem;
  width: 1.4rem;
  margin-right: 0.5rem;
}

.contacts-container {
  display: flex;
  flex-flow: row;
  align-items: center;
}

.contact {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-right: 3rem;
}

.button-container {
  width: 15%;
  margin-left: auto;
  margin-right: 5rem;
  display: flex;
  flex-flow: row;
  align-items: center;

  button {
    @include secondary-button();
    padding-right: 0.7rem;
    padding-left: 0.5rem;
    width: auto;
    display: flex;
    flex-flow: row;
    align-items: center;
  }
}
</style>
