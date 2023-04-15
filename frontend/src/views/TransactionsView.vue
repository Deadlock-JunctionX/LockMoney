<template>
  <AppFrame>
    <div class="pa-4">
      <p class="text-h5">Lịch sử giao dịch</p>

    <div v-if="loading" class="d-flex justify-center">
      <v-progress-circular indeterminate size="72"></v-progress-circular>
    </div>

    <div v-if="!loading" class="mt-2">
      <div v-if="transactions.length == 0">
        Bạn chưa có giao dịch nào được ghi nhận
      </div>

      <div v-if="transactions.length > 0">
        <v-list lines="three">
          <TransactionListItem
            v-for="item in transactions"
            :key="item.id"
            :transaction="item"
          ></TransactionListItem>
        </v-list>
      </div>
    </div>
    </div>
  </AppFrame>
</template>

<script>
import axios from 'axios';
import TransactionListItem from "../components/TransactionListItem";

export default {
  components: {
    TransactionListItem
  },
  data() {
    return {
      transactions: [],
      offset: 0,
      limit: 20,
      loading: false,
      isListEnd: false,
    }
  },
  methods: {
    fetchTransactions(reset) {
      if (reset) {
        this.offset = 0;
      }

      this.loading = true;
      return axios.get("/users/me/transactions/all", {
        params: {
          offset: this.offset,
          limit: this.limit
        }
      })
        .then((response) => {
          if (!reset) {
            this.transactions.push.apply(...response.data.items);
          } else {
            this.transactions = response.data.items;
          }

          if (response.data.items.length < this.limit) {
            this.isListEnd = true
          }
          this.offset += this.limit;
        })
        .catch(() => {})
        .finally(() => {
          this.loading = false;
        })
    }
  },
  mounted() {
    this.fetchTransactions(true);
  }
}
</script>
