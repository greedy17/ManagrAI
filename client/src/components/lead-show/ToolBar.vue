<template>
  <div class="toolbar">
    <div class="top-menu">
      <img class="edit icon" src="@/assets/images/pencil.svg" alt="edit icon" />
      <img class="more icon" src="@/assets/images/more_horizontal.svg" alt="more icon" />
    </div>
    <div class="lead-name">
      <h2>{{ lead.name }}</h2>
    </div>
    <div class="rank">
      <LeadRank :label="true" :rank="lead.rank" />
    </div>
    <div class="lead-lists">
      <div class="header">Lists</div>
      <div class="container">
        <LeadList
          class="list"
          v-for="list in lead.lists"
          :key="list.id"
          :listName="list.title"
          :dark="true"
        />
      </div>
    </div>
    <!--- focus --- -->
    <div class="account-link">Account</div>
    <div class="amount section-shadow">Amount: {{ formattedAmount }}</div>
    <!--- focus --- -->
    <div class="contacts">
      <div class="header section-shadow">
        <span>Contacts</span>
      </div>
      <div class="contacts-container">
        <div class="contact section-shadow" v-for="contact in exampleContacts" :key="contact.id">
          <img src="@/assets/images/sara-smith.png" alt="contact image" />
          <span class="name">{{ contact.name }}</span>
          <div class="phone button">
            <img class="icon" src="@/assets/images/telephone.svg" alt="telephone icon" />
          </div>
          <div class="email button">
            <img class="icon" src="@/assets/images/email.svg" alt="telephone icon" />
          </div>
        </div>
      </div>
    </div>
    <div class="files">
      <div class="header section-shadow">
        <span>Files</span>
      </div>
      <div class="files-container">
        <div class="file section-shadow" v-for="file in exampleFiles" :key="file">
          <img class="icon" src="@/assets/images/document.svg" alt="file icon" />
          {{ file }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LeadRank from '@/components/shared/LeadRank'
import LeadList from '@/components/shared/LeadList'
import currencyFormatter from '@/services/currencyFormatter'
const exampleFiles = ['Filename.pdf', 'filename2.pdf', 'filename3.jpeg']
const exampleContacts = [
  { id: 1, name: 'Sara Smith' },
  { id: 2, name: 'Jake Murray' },
]
export default {
  name: 'ToolBar',
  components: {
    LeadRank,
    LeadList,
  },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return { exampleFiles, exampleContacts }
  },
  computed: {
    formattedAmount() {
      return currencyFormatter.format(this.lead.amount)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.toolbar {
  background-color: white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);

  width: 100%;
  display: flex;
  flex-flow: column;

  .section-shadow {
    box-shadow: 0 1px 0 0 #ececee;
  }
}

.toolbar,
.toolbar > * {
  font-family: $base-font-family, $backup-base-font-family;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 14px;
}

.top-menu {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 34px;
  padding: 0 12px;

  .icon {
    height: 20px;
    opacity: 0.4;
  }

  .edit {
    margin-right: auto;
  }

  .more {
    margin-left: auto;
  }
}

.lead-name {
  padding: 0 15%;
  text-align: center;
}

.rank {
  display: flex;
  flex-flow: row;
  justify-content: center;
}

.lead-lists {
  padding: 20px 20px 10px 20px;
  border-bottom: 5px solid $coral;

  .header {
    margin-bottom: 10px;
  }

  .container {
    display: flex;
    flex-flow: column;

    .list {
      margin-bottom: 10px;
      height: 28px;
    }
  }
}

.account-link {
  height: 48px;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;

  color: $dark-green;
  text-decoration: underline;
}

.amount {
  height: 48px;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;

  font-size: 18px;
}

.section-shadow {
  box-shadow: 0 1px 0 0 #ececee;
}

.contacts {
  .header {
    padding-left: 20px;
    height: 54px;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      font-weight: bold;
    }
  }
  .contact {
    display: flex;
    flex-flow: row;
    align-items: center;
    height: 48px;
    padding-left: 20px;
    font-size: 14px;

    img {
      height: 20px;
      border-radius: 50%;
      margin-right: 15px;
    }

    .phone {
      margin-left: auto;
    }

    .email {
      margin: 0 10px;
    }

    .button {
      @include pointer-on-hover();
      height: 30px;
      width: 30px;
      background-color: #efeff5;
      border-radius: 5px;
      display: flex;
      flex-flow: row;
      align-items: center;
      justify-content: center;

      .icon {
        height: 16px;
        margin: auto;
      }

      .email {
        margin-left: 10px;
      }

      .phone {
        margin-left: auto;
      }
    }
  }
}

.files {
  .header {
    padding-left: 20px;
    height: 54px;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      font-weight: bold;
    }
  }
  .file {
    display: flex;
    flex-flow: row;
    align-items: center;
    height: 48px;
    padding-left: 20px;
    font-size: 14px;

    .icon {
      height: 20px;
      opacity: 0.6;
      margin-right: 15px;
    }
  }
}
// div {
//   border: 1px dashed black;
// }
</style>
