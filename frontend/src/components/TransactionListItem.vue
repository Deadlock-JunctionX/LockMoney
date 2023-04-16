<template>
  <div>
    <v-list-item @click="showDialog = true">
      <template v-slot:prepend>
        <v-icon :icon="icon" size="28" :color="themeColor"></v-icon>
      </template>
      <v-list-item-title :style="`color: ${themeColor}`">
        <b>{{ amount }}</b>
      </v-list-item-title>
      <v-list-item-subtitle>
        <div style="text-transform: uppercase">
          {{ partnerName }}
        </div>
        <div>
          {{ createdAt }}
        </div>
      </v-list-item-subtitle>
    </v-list-item>

    <v-dialog
      v-model="showDialog"
      width="300"
    >
      <v-card flat>
        <v-card-title :style="`color: ${themeColor}`">
          {{ amount }}
        </v-card-title>

        <v-card-subtitle>
          <p>{{ createdAt }}</p>
        </v-card-subtitle>

        <v-card-text>
          <p>{{ transactionAction }} {{ partnerName }}</p>
          <p>
            <b>{{ partnerLocation }}</b>

            <br v-if="partnerDetails">
            <span v-if="partnerDetails">
              {{ partnerDetails }}
            </span>
          </p>

          <p class="text-overline" v-if="transaction.description">
            {{ transaction.description}}
          </p>

          <p v-if="transaction.trusted_app_id" class="text-caption" style="color: #536DFE">
            <br>
            Giao dịch thực hiện qua Lock.Chat
          </p>

          <p style="font-size: 8pt" class="mt-4">
            ID: {{ transaction.id }}
          </p>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    transaction: {
      type: Object,
    }
  },
  data() {
    return {
      showDialog: false,
    }
  },
  computed: {
    createdAt() {
      return this.transaction.created_at;
    },
    context() {
      return this.transaction.current_user_context;
    },
    partnerName() {
      if (this.context == "INCOMING") {
        return this.transaction.from_name
      } else {
        return this.transaction.to_name
      }
    },
    themeColor() {
      if (this.context == "INCOMING") {
        return "#2eb333"
      } else {
        return "#d46820"
      }
    },
    sign() {
      if (this.context == "OUTGOING") {
        return "-"
      }
      return ""
    },
    icon() {
      if (this.context == "INCOMING") {
        return "mdi-arrow-top-left"
      } else {
        return "mdi-arrow-bottom-right"
      }
    },
    partnerLocation() {
      if (this.context == "INCOMING") {
        return this.transaction.from_bank || "Ví LockMoney"
      } else {
        return this.transaction.to_bank || "Ví LockMoney"
      }
    },
    partnerDetails() {
      if (this.context == "INCOMING") {
        if (this.transaction.from_bank_account_number) {
          return `STK: ${this.transaction.from_bank_account_number}`
        }
        return ""
      } else {
        if (this.transaction.to_bank_account_number) {
          return `STK: ${this.transaction.to_bank_account_number}`
        }
        return ""
      }
    },
    transactionAction() {
      if (this.context == "INCOMING") {
        return "Nhận tiền từ"
      } else {
        return "Chuyển tiền tới"
      }
    },
    amount() {
      const formatter = new Intl.NumberFormat()
      return `${this.sign}${formatter.format(this.transaction.amount)} VND`
    }
  }
}
</script>
