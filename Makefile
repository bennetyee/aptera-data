all:	aptera_data coupon_round extract_coupon_investments

aptera_data: any
	ln -f $^ $@

coupon_round: any
	ln -f $^ $@

extract_coupon_investments: any
	ln -f $^ $@

# cat is needed because otherwise zip seeks to beginning of file and
# overwrites the #! string
any:	*.py
	rm -f any; (echo '#!/usr/bin/python3'; zip - $^) | cat > $@ && chmod +x $@

clean:
	rm -f aptera_data coupon_round extract_coupon_investments any.zip any *~

.PHONY:	clean all
